import json
import os
import threading

from connect import __version__
from connect.output import Task
from connect import convert
from connect.socks import socks
from connect.team_server.models import AgentModel, ImplantModel, TaskModel

from flask_socketio import emit, disconnect

class TeamServerEvents:

    def __init__(self, db, sio_server, task_manager, team_server_uri, key):
        self.key = key
        self.db = db
        self.socks_proxies = {}
        self.sio_server = sio_server
        self.team_server_uri = team_server_uri
        self.task_manager = task_manager

    def commit(self, models: list):
        """
        Commits model object changes to the database.
        :param models: A list of models.
        """
        for model in models:
            self.db.session.add(model)
        self.db.session.commit() 

    def connect(self, auth):
        """
        This event is triggered on client connection requests.
        If the authentication data does not match the generated key,
        then a disconnect event is triggered.
        :param auth:
        """
        if not auth == self.key:
            disconnect()

    def agents(self, data):
        """
        Emit all available agents.
        """
        agents = [agent.get_agent() for agent in AgentModel.query.all()]
        self.sio_server.emit('agents', {'agents': agents, 'all': data['all']})

    def implants(self, data):
        """
        Emit all available implants.
        """
        if not data:
            implants = [implant.get_implant() for implant in ImplantModel.query.all()]
            self.sio_server.emit('implants', {'implants': implants})
            return
        
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            emit('error', 'Invalid JSON provided to implants event')
            return

        action = data.get('action')
        if action == 'create':
            implant = ImplantModel.query.filter_by(name=data.get('name')).first()
            if implant:
                emit('error', f'Failed to create implant \'{implant.name}\' name already in use.')
                return
            new_implant = ImplantModel(options=data.get('options'), name=data.get('name'))
            self.db.session.add(new_implant)
            self.db.session.commit()
            new_implant_dict = {
                'name': new_implant.name,
                'id': new_implant.id,
                'key': new_implant.key
            }
            emit('success', f'Implant created successfully {new_implant_dict}')
        elif action == 'delete':
            implant_id = data.get('implant_id')
            if implant_id:
                if implant_id == 'all':
                    for implant in ImplantModel.query.all():
                        if implant.agents:
                            emit('error', f'Failed to delete implant. There are {len(implant.agents)} agent(s) connected to {implant.id}.')
                            continue
                        emit('success', f'Implant {implant.id} deleted successfully')
                        self.db.session.delete(implant)
                        self.db.session.commit()
                        
                else:
                    implant = ImplantModel.query.filter_by(id=implant_id).first()
                    if not implant:
                        emit('error', 'Implant not found')
                        return
                    if implant.agents:
                        emit('error', f'Failed to delete implant. There are {len(implant.agents)} agent(s) connected to {implant.id}.')
                        return
                    self.db.session.delete(implant)
                    self.db.session.commit()
                    emit('success', 'Implant deleted successfully')
            else:
                emit('error', 'No implant ID provided for delete')
        else:
            emit('error', 'Invalid action provided')

    def socks(self, data):
        if not data:
            self.sio_server.emit('success', {'socks': self.socks_proxies})
            return
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            emit('error', 'Invalid JSON provided to socks event')
            return
        try:
            action = data.get('action')
            address = data.get('address')
            port = int(data.get('port'))
            if action == 'local':
                proxy = socks.Proxy(address, port, self.team_server_uri, self.key)
                t = threading.Thread(target=proxy.run)
                t.daemon = True
                t.start()
            elif action == 'remote':
                agent_id = data.get('agent_id')
                proxy = socks.Proxy(address, port, self.team_server_uri, self.key, agent_id=agent_id)
                t = threading.Thread(target=proxy.run)
                t.daemon = True
                t.start()
        except Exception as e:
            self.sio_server.emit('error', f'Failed to parse socks event:\n{e}')

    def task(self, data):
        """
        This event schedules a new task to be sent to the agent.
        The *data* excpeted is {'name':'', 'agent_name':'', 'parameters':'', type:''}
        :param data:
        """
        data = json.loads(data)
        task = Task(*data['task'])
        print(task)
        parameters = task.parameters
        for index, parameter in enumerate(parameters):
            if os.path.exists(parameter):
                with open(parameter, 'rb') as fd:
                    parameters[index], key = convert.xor_base64(fd.read())
                parameters = [*parameters[:index], parameters[index], key, *parameters[index+1:]]
        parameters = ','.join([convert.string_to_base64(parameter) for parameter in parameters])
        agent = AgentModel.query.filter_by(name=data['agent']).first()
        task = TaskModel(name=task.name, description=task.description, parameters=parameters, type=task.type,  agent=agent)
        self.commit([task])
        print('commited')

    def version(self):
        emit('information', f'The current version is {__version__}')