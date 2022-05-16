from . import models

from connect.output import error, print_traceback

from flask import Flask
from flask_socketio import SocketIO


class TeamServer(object):
    """
    A WebSocket Flask App Wrapper.
    """

    def __init__(self, name, config, db, websocket):
        self.app = Flask(name)
        self.app.config.from_object(config)
        self.websocket = websocket
        self.db = db

    def create_database(self):
        self.db.init_app(self.app)
        with self.app.app_context():
            self.db.create_all()

    def add_event(self, message, handler):
        self.websocket.on_event(message, handler)

    def add_blueprint(self, blueprint):
        self.app.register_blueprint(blueprint)

    def add_stager(self, stager):
        with self.app.app_context():
            self.db.session.add(stager)
            self.db.session.commit()

    def drop_stagers(self):
        with self.app.app_context():
            self.db.session.query(models.StagerModel).delete()
            self.db.session.commit()

    def run(self, ip, port):
        try:
            self.websocket.init_app(self.app)
            self.websocket.run(self.app, host=ip, port=port)
        except PermissionError:
            error(f'Failed to start team server on port {port}: Permission Denied.')
        except Exception:
            print_traceback()
