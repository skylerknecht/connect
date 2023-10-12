import asyncio
import socketio
from aiohttp import web
from connect.server.models import AgentModel, get_session
from connect.server.tasks import TaskManager
from .events import ListenerEvents
from .routes import ListenerRoutes


class ConnectListener:

    def __init__(self, ip, port, socks_manager, sio_team_server):
        """
        Initialize a new Connect Listener

        Args:
            ip (str): The IP address or hostname of the server.
            port (int): The port number to connect to on the server.
            socks_manager: Manager to create and shutdown socks servers.
        """
        self.ip = ip
        self.port = port
        self.sio_team_server = sio_team_server

        self.sio_server = socketio.AsyncServer(async_mode='aiohttp')
        task_manager = TaskManager(self.sio_team_server)
        self.listener_events = ListenerEvents(self.sio_server, self.sio_team_server, task_manager, socks_manager)
        self.application = web.Application()
        self.listener_routes = ListenerRoutes(self.application, self.sio_team_server, task_manager)
        self.socks_manager = socks_manager

        self.loop = asyncio.get_event_loop()
        self.runner = web.AppRunner(self.application)
        self.site = None

        self.asyncio_tasks = []

    async def start(self):
        self.sio_server.attach(self.application)
        self.asyncio_tasks.append(self.loop.create_task(self.ping()))
        self.asyncio_tasks.append(self.loop.create_task(self.send_tasks()))
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.ip, self.port)
        await self.site.start()

    async def stop(self):
        for task in self.asyncio_tasks:
            task.cancel()
        await self.site.stop()
        await self.runner.cleanup()

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
                    for task in self.socks_manager.get_socks_tasks(agent.id):
                        await self.sio_server.emit(task.event, task.data, room=sid)
                    await self.sio_server.emit('tasks', agent.get_tasks(session), room=sid)
            await self.sio_server.sleep(0.1)