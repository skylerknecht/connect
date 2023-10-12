import json
import datetime
import threading
import random

from connect.server.models import AgentModel, get_session


class ListenerEvents:

    def __init__(self, sio_server, sio_team_server, task_manager, socks_manager):
        self.socks_manager = socks_manager
        self.sio_team_server = sio_team_server
        self.sio_server = sio_server
        self.sio_server.on('socks', self.socks)
        self.sio_server.on('socks_connect_results', self.socks_connect_results)
        self.sio_server.on('socks_downstream_results', self.socks_downstream_results)
        self.sio_server.on('batch_response', self.batch_response)
        self.sio_server.on('connect', self.connect)
        self.sio_server.on('disconnect', self.disconnect)
        self.sio_server.on('pong', self.pong)
        self.task_manager = task_manager
        self.agent_id_to_sid = {}
        self.sid_to_agent_id = {}

    async def connect(self, sid, environ, auth: str = ''):
        with get_session() as session:
            agent = session.query(AgentModel).filter_by(check_in_task_id=auth).first()
            if not agent:
                await self.sio_server.disconnect(sid)
                return
            self.agent_id_to_sid[agent.id] = sid
            self.sid_to_agent_id[sid] = agent.id
            await self.sio_team_server.emit('success', f'Agent {agent.id} is interactive')

    async def disconnect(self, sid):
        try:
            agent_id = self.sid_to_agent_id[sid]
            del self.sid_to_agent_id[sid]
            del self.agent_id_to_sid[agent_id]
            await self.sio_team_server.emit('information', f'Agent {agent_id} is no longer interactive')
        except:
            pass

    async def pong(self, sid):
        with get_session() as session:
            agent = session.query(AgentModel).filter_by(id=self.sid_to_agent_id[sid]).first()
            agent.check_in = datetime.datetime.now()
            session.add(agent)

    async def batch_response(self, sid, data):
        await self.task_manager.parse_batch_response([data])

    async def socks(self, sid):
        agent_id = self.sid_to_agent_id[sid]
        if agent_id in self.socks_manager.socks_servers:
            await self.sio_team_server.emit('information', f'Attempting to shutdown socks server for Agent {agent_id}')
            await self.socks_manager.shutdown_socks_server(agent_id, self.sio_team_server)
        else:
            await self.sio_team_server.emit('information', f'Attempting to start socks server for Agent {agent_id}')
            await self.socks_manager.create_socks_server(agent_id, '127.0.0.1', random.randint(9050, 9100), self.sio_team_server)

    async def socks_connect_results(self, sid, results):
        threading.Thread(
            target=self.socks_manager.handle_socks_task_results,
            args=('socks_connect', json.loads(results),),
            daemon=True
        ).start()

    async def socks_downstream_results(self, sid, results):
        self.socks_manager.handle_socks_task_results('socks_downstream', json.loads(results))
