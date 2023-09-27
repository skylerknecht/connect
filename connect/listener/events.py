import json
import datetime
from connect.server.models import AgentModel


class ListenerEvents:

    def __init__(self, sio_server, sio_client, task_manager, session):
        self.session = session
        self.sio_client = sio_client
        self.sio_server = sio_server
        self.sio_server.on('batch_response', self.batch_response)
        self.sio_server.on('connect', self.connect)
        self.sio_server.on('disconnect', self.disconnect)
        self.sio_server.on('pong', self.pong)
        self.task_manager = task_manager
        self.agent_id_to_sid = {}
        self.sid_to_agent_id = {}

    async def connect(self, sid, environ, auth: str = ''):
        agent = self.session.query(AgentModel).filter_by(check_in_task_id=auth).first()
        if not agent:
            await self.sio_server.disconnect(sid)
            return
        self.agent_id_to_sid[agent.id] = sid
        self.sid_to_agent_id[sid] = agent.id
        self.sio_client.emit('proxy', json.dumps(['success', f'Agent {agent.id} is interactive.']))

    async def disconnect(self, sid):
        agent = self.session.query(AgentModel).filter_by(id=self.sid_to_agent_id[sid]).first()
        if not agent:
            return
        agent_id = self.sid_to_agent_id[sid]
        del self.sid_to_agent_id[sid]
        del self.agent_id_to_sid[agent_id]
        self.sio_client.emit('proxy', json.dumps(['information', f'Agent {agent.id} no longer interactive.']))

    def pong(self, sid):
        agent = self.session.query(AgentModel).filter_by(id=self.sid_to_agent_id[sid]).first()
        agent.check_in = datetime.datetime.now()
        self.session.add(agent)
        self.session.commit()

    async def batch_response(self, sid, data):
        self.task_manager.parse_batch_response([data])