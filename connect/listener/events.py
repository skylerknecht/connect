import json
import datetime
import threading
import random

from connect.server.models import AgentModel, get_session


class ListenerEvents:

    def __init__(self, sio_server, sio_team_server, task_manager, stream_server_manager):
        self.sio_team_server = sio_team_server
        self.sio_server = sio_server
        self.sio_server.on('stream_connect_results', self.stream_connect_results)
        self.sio_server.on('stream_disconnect_results', self.stream_disconnect_results)
        self.sio_server.on('stream_downstream_results', self.stream_downstream_results)
        self.sio_server.on('batch_response', self.batch_response)
        self.sio_server.on('connect', self.connect)
        self.sio_server.on('disconnect', self.disconnect)
        self.sio_server.on('pong', self.pong)
        self.task_manager = task_manager
        self.stream_server_manager = stream_server_manager
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

    async def stream_connect_results(self, sid, results):
        agent_id = self.sid_to_agent_id[sid]
        await self.stream_server_manager.handle_stream_connect(agent_id, results)

    async def stream_disconnect_results(self, sid, results):
        agent_id = self.sid_to_agent_id[sid]
        await self.stream_server_manager.handle_stream_disconnect(agent_id, results)

    async def stream_downstream_results(self, sid, results):
        agent_id = self.sid_to_agent_id[sid]
        self.stream_server_manager.handle_stream_downstream(agent_id, results)
