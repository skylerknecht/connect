import argparse
import os

from . import events
from . import models
from . import views
from connect import generate
from connect import output
from flask import Flask


class FlaskServerBase:
    NAME = 'untitled'

    def __init__(self):
        self.app = Flask(self.NAME)
        self.setup_environment_keys()
        self.app.config.from_pyfile(f'{os.getcwd()}/connect/server/settings.py')
        models.db.init_app(self.app)
        with self.app.app_context():
            models.db.metadata.reflect(models.db.engine)
            if not models.db.metadata.tables:
                models.db.create_all()

    def run(self, arguments):
        raise NotImplementedError('The {self.NAME} has not implemented run.')

    @staticmethod
    def setup_environment_keys():
        if not os.path.exists('.env'):
            print(f'Creating environment file {os.getcwd()}/.env')
            with open('.env', 'w') as fd:
                print(f'Writing database SECRET_KEY')
                fd.write(f'SECRET_KEY={generate.string_identifier(30)}')

    def setup_parser(self, subparser):
        raise NotImplementedError('The {self.NAME} has not implemented setup_parser.')


class TeamServer(FlaskServerBase):
    def __init__(self):
        self.NAME = 'team_server'
        super().__init__()
        events.sio.init_app(self.app)

    def setup_parser(self, subparser):
        parser = subparser.add_parser(self.NAME, help='The Connect Team Server',
                                      formatter_class=argparse.RawTextHelpFormatter, usage=argparse.SUPPRESS)
        parser.add_argument('ip', metavar='ip', help='Server ip.')
        parser.add_argument('port', metavar='port', help='Server port.')
        parser.add_argument('--ssl', nargs=2, metavar=('CERT', 'KEY'), help='Use SSL.')
        parser.add_argument('--debug', action='store_true', help='Enable debug mode.')


class HTTPListener(FlaskServerBase):
    def __init__(self):
        self.NAME = 'http_listener'
        super().__init__()
        self.app.register_blueprint(views.check_in_blueprint)

    def run(self, arguments):
        try:
            # if arguments:
            #     events.socketio.run(self.app, host=ip, port=port, keyfile=keyfile, certfile=certfile)
            #     return
            self.app.run(host=arguments.ip, port=arguments.port)
        except PermissionError:
            output.display('ERROR', f'Failed to start team server on port {arguments.port}: Permission Denied.')

    def setup_parser(self, subparser):
        parser = subparser.add_parser(self.NAME, help='The Connect HTTP Listener',
                                      formatter_class=argparse.RawTextHelpFormatter, usage=argparse.SUPPRESS)
        parser.add_argument('ip', metavar='ip', help='Server ip.')
        parser.add_argument('port', metavar='port', help='Server port.')
        parser.add_argument('--ssl', nargs=2, metavar=('CERT', 'KEY'), help='Use SSL.')
        parser.add_argument('--debug', action='store_true', help='Enable debug mode.')


class SocketIOListener(FlaskServerBase):
    def __init__(self):
        self.NAME = 'socketio_listener'
        super().__init__()
        events.sio.init_app(self.app)

    def run(self, arguments):
        try:
            # if arguments: #ToDo: does ssl really affect SocketIO?
            #     events.socketio.run(self.app, host=ip, port=port, keyfile=keyfile, certfile=certfile)
            #     return
            events.sio.run(self.app, host=arguments.ip, port=arguments.port)
        except PermissionError:
            output.display('ERROR', f'Failed to start team server on port {arguments.port}: Permission Denied.')
    def setup_parser(self, subparser):
        parser = subparser.add_parser(self.NAME, help='The Connect SocketIO Listener',
                                      formatter_class=argparse.RawTextHelpFormatter, usage=argparse.SUPPRESS)
        parser.add_argument('ip', metavar='ip', help='Server ip.')
        parser.add_argument('port', metavar='port', help='Server port.')
        parser.add_argument('--ssl', nargs=2, metavar=('CERT', 'KEY'), help='Use SSL.')
        parser.add_argument('--debug', action='store_true', help='Enable debug mode.')
