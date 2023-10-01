import asyncio
import json
import time
import socketio

from . import events
from . import routes
from aiohttp import web
from connect.server import tasks
from connect.server.models import AgentModel, get_session

class ConnectListener:
    NAME = 'Connect Listener'

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.application = web.Application()
        self.sio_client = socketio.Client()
        self.sio_server = socketio.AsyncServer(async_mode='aiohttp', async_handlers=True)
        self.loop = asyncio.new_event_loop()
        task_manager = tasks.TaskManager(self.sio_client)
        self.listener_routes = routes.ListenerRoutes(self.application, self.sio_client, task_manager)
        self.listener_events = events.ListenerEvents(self.sio_server, self.sio_client, task_manager)

    async def ping(self):
        while True:
            await self.sio_server.sleep(1)
            await self.sio_server.emit('ping')

    async def send_tasks(self):
        while True:
            with get_session() as session:
                agents = session.query(AgentModel).all()
                for agent in agents:
                    sid = self.listener_events.agent_id_to_sid.get(agent.id, None)
                    if not sid:
                        continue
                    await self.sio_server.emit('tasks', agent.get_tasks(session), room=sid)
            await self.sio_server.sleep(1)

    def run(self, team_server_uri, team_server_key):
        self.sio_client.connect(team_server_uri, auth=team_server_key)
        self.sio_server.attach(self.application)
        runner = web.AppRunner(self.application)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(runner.setup())
        loop.create_task(self.ping())
        loop.create_task(self.send_tasks())
        try:
            self.sio_client.emit('proxy', json.dumps(['information', f'Starting HTTP listener on {self.ip}:{self.port}']))
            site = web.TCPSite(runner, self.ip, self.port)
            loop.run_until_complete(site.start())
            loop.run_forever()
        except PermissionError:
            self.sio_client.emit('proxy', json.dumps(['error', f'Failed to start HTTP listener on {self.ip}:{self.port}, Permission Denied.']))
        except OSError as e:
            if e.errno == 98:
                self.sio_client.emit('proxy', json.dumps(
                    ['error', f'Failed to start HTTP listener on {self.ip}:{self.port}, Address Already In Use.']))
                return
            self.sio_client.emit('proxy', json.dumps(
                ['error', f'Failed to start HTTP listener on {self.ip}:{self.port}:\n{e}']))

