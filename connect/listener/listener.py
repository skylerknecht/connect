import asyncio
import json
import time
import socketio

from . import events
from . import routes
from aiohttp import web
from connect.server import tasks
from connect.server import models

class ConnectListener:
    NAME = 'Connect Listener'

    def __init__(self, session):
        self.session = session
        self.application = web.Application()
        self.sio_client = socketio.Client()
        self.sio_server = socketio.AsyncServer(async_mode='aiohttp', async_handlers=True)
        self.loop = asyncio.new_event_loop()
        task_manager = tasks.TaskManager(self.sio_client, session)
        self.listener_routes = routes.ListenerRoutes(self.application, self.sio_client, task_manager, session)
        self.listener_events = events.ListenerEvents(self.sio_server, self.sio_client, task_manager, session)

    async def ping(self):
        while True:
            await self.sio_server.sleep(1)
            await self.sio_server.emit('ping')

    async def send_tasks(self):
        while True:
            agents = self.session.query(models.AgentModel).all()
            for agent in agents:
                sid = self.listener_events.agent_id_to_sid.get(agent.id, None)
                if not sid:
                    continue
                await self.sio_server.emit('tasks', agent.get_tasks(),room=sid)
            await self.sio_server.sleep(1)

    def run(self, team_server_uri, team_server_key, ip, port):
        self.sio_client.connect(team_server_uri, auth=team_server_key)
        self.sio_server.attach(self.application)
        runner = web.AppRunner(self.application)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(runner.setup())
        loop.create_task(self.ping())
        loop.create_task(self.send_tasks())
        try:
            self.sio_client.emit('proxy', json.dumps(['information', f'Starting HTTP listener on {ip}:{port}']))
            site = web.TCPSite(runner, ip, port)
            loop.run_until_complete(site.start())
            loop.run_forever()
        except PermissionError:
            self.sio_client.emit('proxy', json.dumps(['error', f'Failed to start HTTP listener on {ip}:{port}, Permission Denied.']))

