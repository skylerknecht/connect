import asyncio
import socketio

from . import events
from aiohttp import web
from connect.generate import string_identifier
from connect.output import display


class TeamServer:
    NAME = 'Connect Team Server'

    def __init__(self):
        self.application = web.Application()
        self.key = string_identifier()
        self.sio_server = socketio.AsyncServer(async_mode='aiohttp', max_http_buffer_size=100*1024*1024*1024)

    def run(self, arguments):
        events.TeamServerEvents(f'http://{arguments.ip}:{arguments.port}/', self.key, self.sio_server)
        self.sio_server.attach(self.application)
        runner = web.AppRunner(self.application)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(runner.setup())
        try:
            display(f'Starting {self.NAME} on {arguments.ip}:{arguments.port}', 'INFORMATION')
            display(f'The super secret key {self.key}', 'INFORMATION')
            site = web.TCPSite(runner, arguments.ip, arguments.port)
            loop.run_until_complete(site.start())
            loop.run_forever()
        except PermissionError:
            display(f'Failed to start {self.NAME} on port {arguments.port}: Permission Denied.', 'ERROR')
