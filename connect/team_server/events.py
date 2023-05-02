import json
import os
import traceback
import datetime


from connect import __version__, generate
from connect.output import Task
from connect import convert
from connect.team_server.models import AgentModel, ImplantModel, TaskModel
from flask_socketio import emit, disconnect


class TeamServerEvents:

    def __init__(self, db, sio_server, key, socks_proxy_manager):
        self.db = db
        self.sio_server = sio_server
        self.key = key
        self.socks_proxy_manager = socks_proxy_manager

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
        emit('agents', {'agents': agents, 'all': data['all']}, broadcast=False)

    def implants(self, data):
        """
        Emit all available implants.
        """

        # ToDo: Add server-side input checks to avoid unnecessary errors.
        if not data:
            implants = [implant.get_implant() for implant in ImplantModel.query.all()]
            self.sio_server.emit('implants', {'implants': implants})
            return

        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            emit('error', 'Invalid JSON provided to implants event', broadcast=False)
            return

        action = data.get('action')
        if action == 'create':
            implant = ImplantModel.query.filter_by(name=data.get('name')).first()
            if implant:
                emit('error', f'Failed to create implant \'{implant.name}\' name already in use.', broadcast=False)
                return
            new_implant = ImplantModel(options=data.get('options'), name=data.get('name'), location=data.get('location'))
            self.db.session.add(new_implant)
            self.db.session.commit()
            emit('success', f'Successfully created key, \'{new_implant.key}\' for implant \'{new_implant.name}\'. ', broadcast=False)
        elif action == 'delete':
            implant_id = data.get('implant_id')
            if implant_id:
                if implant_id == 'all':
                    for implant in ImplantModel.query.all():
                        if implant.agents:
                            emit('error',
                                 f'Failed to delete implant. There are {len(implant.agents)} agent(s) connected to {implant.id}.', broadcast=False)
                            continue
                        emit('success', f'Implant {implant.id} deleted successfully', broadcast=False)
                        self.db.session.delete(implant)
                        self.db.session.commit()
                else:
                    implant = ImplantModel.query.filter_by(id=implant_id).first()
                    if not implant:
                        emit('error', 'Implant not found')
                        return
                    if implant.agents:
                        emit('error',
                             f'Failed to delete implant. There are {len(implant.agents)} agent(s) connected to {implant.id}.', broadcast=False)
                        return
                    self.db.session.delete(implant)
                    self.db.session.commit()
                    emit('success', 'Implant deleted successfully', broadcast=False)
            else:
                emit('error', 'No implant ID provided for delete', broadcast=False)
        else:
            emit('error', 'Invalid action provided', broadcast=False)

    def socks(self, data):
        try:
            if not data:
                emit('socks', {'socks': self.socks_proxy_manager.proxy_server_info}, broadcast=False)
                return
        except:
            emit('error', f'Failed to retrieve socks proxy server information:', broadcast=False)
            emit('default', traceback.format_exc(), broadcast=False)
            return

        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            emit('error', f'Failed to parse JSON data for socks request:', broadcast=False)
            emit('default', traceback.format_exc(), broadcast=False)
            return

        action = data.get('action') if 'action' in data.keys() else None
        socks_id = data.get('proxy_id') if 'proxy_id' in data.keys() else None
        address = data.get('address') if 'address' in data.keys() else None
        port = data.get('port') if 'port' in data.keys() else None
        agent_id = data.get('agent_id') if 'agent_id' in data.keys() else None

        if not action:
            emit('error', 'The following socks request has no action:', broadcast=False)
            emit('default', data, broadcast=False)
            return

        try:
            if action == 'local' or action == 'remote':
                self.socks_proxy_manager.create_proxy(address, int(port), agent_id=agent_id)
                emit('success', f'Created {action} proxy on {address}:{port}.', broadcast=False)
            if action == 'shutdown':
                if not socks_id:
                    emit('error', 'The following socks shutdown request has no socks_id:', broadcast=False)
                    emit('default', data, broadcast=False)
                    return
                self.socks_proxy_manager.shutdown_proxy_server(int(socks_id))
                emit('information', f'Scheduled {socks_id} to shutdown, this may take awhile.', broadcast=False)
        except:
            emit('error', f'Failed to process socks request:', broadcast=False)
            emit('default', traceback.format_exc(), broadcast=False)

    def task(self, data):
        """
        This event schedules a new task to be sent to the agent.
        The *data* excepted is {'name':'', 'agent_name':'', 'parameters':'', type:''}
        :param data:
        """

        # ToDo: Load module task scheduling for modules that aren't in 'agent.loaded_modules'.
        """
        We would look up the method within agent.available_modules to retrieve the module path
        and if the MD5 hash of the module is not in agent.loaded_modules then schedule it to be
        loaded. 
        """

        data = json.loads(data)
        agent = AgentModel.query.filter_by(name=data['agent']).first()
        task = Task(*data['task'])
        module = data['module'] if 'module' in data.keys() else None
        if module:
            if not os.path.exists(f'{agent.implant.location}{module}'):
                emit('error', f'Module {agent.implant.location}{module} does not exist.', broadcast=False)
                return
            _hash = generate.md5_hash(f'{agent.implant.location}{module}')
            if _hash not in agent.loaded_modules:
                agent.loaded_modules = _hash if not agent.loaded_modules else ','.join(
                    agent.loaded_modules) + f',{_hash}'
                with open(f'{agent.implant.location}{module}', 'rb') as fd:
                    parameters = convert.xor_base64(fd.read())
                parameters = ','.join([convert.string_to_base64(parameter) for parameter in parameters])
                load_task = TaskModel(name='load', description=f'load {module}', parameters=parameters, type='1', agent=agent)
                self.commit([load_task])
        parameters = task.parameters
        for index, parameter in enumerate(parameters):
            if os.path.exists(parameter):
                with open(parameter, 'rb') as fd:
                    parameters[index], key = convert.xor_base64(fd.read())
                parameters = [*parameters[:index], parameters[index], key, *parameters[index + 1:]]
        parameters = ','.join([convert.string_to_base64(parameter) for parameter in parameters])
        task = TaskModel(name=task.name, description=task.description, parameters=parameters, type=task.type,
                         agent=agent)
        # Todo: Find a better way to handle socks_downstream.
        if task.name == 'socks_downstream':
            task.sent = datetime.datetime.fromtimestamp(823879740.0)
        self.commit([task])

    def version(self):
        emit('information', f'The current version is {__version__}', broadcast=False)
