from connect.generate import string_identifier
from connect.output import display
from connect.server.flask_server import FlaskServerBase
from flask_socketio import SocketIO
from . import events


class TeamServer(FlaskServerBase):
    def __init__(self):
        self.NAME = 'team_server'
        super().__init__()
        self.key = string_identifier()
        self.team_server_sio = SocketIO()

    def run(self, arguments):
        self.setup_app()
        events.TeamServerEvents(self.key, self.team_server_sio)
        self.team_server_sio.init_app(self.app)
        try:
            # if arguments: #ToDo: does ssl really affect SocketIO?
            #     events.socketio.run(self.app, host=ip, port=port, keyfile=keyfile, certfile=certfile)
            #     return
            display(f'Starting Team Server on {arguments.ip}:{arguments.port}', 'INFORMATION')
            display(f'The super secret key `{self.key}`', 'INFORMATION')
            self.team_server_sio.run(self.app, host=arguments.ip, port=arguments.port)
        except PermissionError:
            display(f'Failed to start team server on port {arguments.port}: Permission Denied.', 'ERROR')