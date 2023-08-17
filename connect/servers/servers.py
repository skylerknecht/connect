import argparse
import os
import threading

from . import events
from . import models
from . import views
from . import tasks
from connect import generate
from connect.output import display
from flask import Flask
from flask_socketio import SocketIO


class FlaskServerBase:
    NAME = 'untitled'

    def __init__(self):
        self.app = None

    def run(self, arguments):
        raise NotImplementedError(f'The {self.NAME} has not implemented run.')

    def setup_app(self):
        self.app = Flask(self.NAME)
        self.setup_environment_keys()
        self.app.config.from_pyfile(f'{os.getcwd()}/connect/servers/settings.py')
        models.db.init_app(self.app)
        with self.app.app_context():
            if not os.path.exists(f'{os.getcwd()}/instance/connect.db'):
                print('Database does not exist, creating it.')
                models.db.create_all()

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
        self.key = generate.string_identifier()
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

    def setup_parser(self, subparser):
        parser = subparser.add_parser(self.NAME, help='SocketIO Webserver used to retrieve information on agents, '
                                                      'create implants and schedule tasks.',
                                      formatter_class=argparse.RawTextHelpFormatter, usage=argparse.SUPPRESS)
        parser.add_argument('--ip', metavar='ip', help='Server ip.', default='127.0.0.1')
        parser.add_argument('--port', metavar='port', help='Server port.', default=1337)
        parser.add_argument('--ssl', nargs=2, metavar=('CERT', 'KEY'), help='Use SSL.')
        parser.add_argument('--debug', action='store_true', help='Enable debug mode.')


class HTTPListener(FlaskServerBase):
    def __init__(self):
        self.NAME = 'http_listener'
        super().__init__()

    def run(self, arguments):
        self.setup_app()
        task_manager = tasks.TaskManager()
        views.HTTPListenerRoutes(self.app, task_manager)
        try:
            # if arguments:
            #     events.socketio.run(self.app, host=ip, port=port, keyfile=keyfile, certfile=certfile)
            #     return
            self.app.run(host=arguments.ip, port=arguments.port)
        except PermissionError:
            display(f'Failed to start {self.NAME} on port {arguments.port}: Permission Denied.', 'ERROR')

    def setup_parser(self, subparser):
        parser = subparser.add_parser(self.NAME, help='HTTP Listener that implants or agents will check in to.',
                                      formatter_class=argparse.RawTextHelpFormatter, usage=argparse.SUPPRESS)
        parser.add_argument('ip', metavar='ip', help='Server ip.')
        parser.add_argument('port', metavar='port', help='Server port.')
        parser.add_argument('--ssl', nargs=2, metavar=('CERT', 'KEY'), help='Use SSL.')
        parser.add_argument('--debug', action='store_true', help='Enable debug mode.')


class SocketIOListener(FlaskServerBase):
    def __init__(self):
        self.NAME = 'socketio_listener'
        super().__init__()

    def run(self, arguments):
        self.setup_app()
        events.listener_sio.init_app(self.app)
        try:
            # if arguments: #ToDo: does ssl really affect SocketIO?
            #     events.socketio.run(self.app, host=ip, port=port, keyfile=keyfile, certfile=certfile)
            #     return
            events.listener_sio.run(self.app, host=arguments.ip, port=arguments.port)
        except PermissionError:
            display(f'Failed to start {self.NAME} on port {arguments.port}: Permission Denied.', 'ERROR')

    def setup_parser(self, subparser):
        parser = subparser.add_parser(self.NAME, help='SocketIO Listener that implants or agents will check in to.',
                                      formatter_class=argparse.RawTextHelpFormatter, usage=argparse.SUPPRESS)
        parser.add_argument('ip', metavar='ip', help='Server ip.')
        parser.add_argument('port', metavar='port', help='Server port.')
        parser.add_argument('--ssl', nargs=2, metavar=('CERT', 'KEY'), help='Use SSL.')
        parser.add_argument('--debug', action='store_true', help='Enable debug mode.')
