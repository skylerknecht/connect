import os
import logging

from . import models
from connect import output
from flask import Flask


os.environ['WERKZEUG_RUN_MAIN'] = 'true'
log = logging.getLogger('werkzeug')
log.disabled = True


class TeamServerConfig:
    """
    App Config for the team server.
    """
    TEMPLATES_AUTO_RELOAD = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = '463f1eabe8f830653b2ffd8a89cd1272'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///connect.db'
    JSON_SORT_KEYS = False

class TeamServer(object):
    """
    A Flask App Wrapper.
    """

    def __init__(self, name, db, websocket) -> None:
        self.app = Flask(name)
        self.app.config.from_object(TeamServerConfig)
        self.websocket = websocket
        self.db = db

    def create_database(self):
        self.db.init_app(self.app)
        with self.app.app_context():
            self.db.create_all()

    def add_blueprint(self, blueprint):
        self.app.register_blueprint(blueprint)

    def add_event(self, event, function):
        self.websocket.on_event(event, function)

    def add_route(self, route, name, function, methods=['GET']):
        self.app.add_url_rule(route, name, function, methods=methods)


    def run(self, ip, port):
        try:
            self.websocket.init_app(self.app)
            self.websocket.run(self.app, host=ip, port=port)
        except PermissionError:
            output.display('ERROR', f'Failed to start team server on port {port}: Permission Denied.')
        except Exception as e:
            output.display('DEFAULT', e)