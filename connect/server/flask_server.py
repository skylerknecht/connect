import flask
import logging
import os

from . import models
from connect import generate
from connect.output import display


class FlaskServerBase:
    NAME = 'untitled'

    def __init__(self):
        self.app = None

    def run(self, arguments):
        raise NotImplementedError(f'The {self.NAME} has not implemented run.')

    def setup_app(self):
        flask.cli.show_server_banner = lambda *args: None
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        self.app = flask.Flask(self.NAME)
        self.setup_environment_keys()
        self.app.config.from_pyfile(f'{os.getcwd()}/connect/server/settings.py')
        models.db.init_app(self.app)
        with self.app.app_context():
            if not os.path.exists(f'{os.getcwd()}/instance/connect.db'):
                display('Database does not exist, creating it.', 'INFORMATION')
                models.db.create_all()

    @staticmethod
    def setup_environment_keys():
        if not os.path.exists(f'{os.getcwd()}/instance/.key'):
            display(f'Creating key file {os.getcwd()}/instance/.key', 'INFORMATION')
            with open(f'{os.getcwd()}/instance/.key', 'w') as fd:
                fd.write(f'{generate.string_identifier(30)}')


