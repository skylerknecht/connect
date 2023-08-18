import os


from . import models
from connect import generate
from flask import Flask


class FlaskServerBase:
    NAME = 'untitled'

    def __init__(self):
        self.app = None

    def run(self, arguments):
        raise NotImplementedError(f'The {self.NAME} has not implemented run.')

    def setup_app(self):
        self.app = Flask(self.NAME)
        self.setup_environment_keys()
        self.app.config.from_pyfile(f'{os.getcwd()}/connect/server/settings.py')
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


