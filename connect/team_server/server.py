from connect.output import print_error, print_traceback

from flask import Flask


class TeamServer(object):
    """
    A WebSocket Flask App Wrapper.
    """

    def __init__(self, name, config, db, login_manager, websocket):
        self.app = Flask(name, template_folder='connect/team_server/templates', static_folder='connect/team_server/static')
        self.app.config.from_object(config)
        self.login_manager = login_manager
        self.websocket = websocket
        self.db = db

    def add_event(self, message, handler):
        self.websocket.on_event(message, handler)

    def add_blueprint(self, blueprint):
        self.app.register_blueprint(blueprint)

    def create_database(self):
        self.db.init_app(self.app)
        with self.app.app_context():
            self.db.create_all()
        
    def run(self, ip: str, port: int):
        try:
            self.websocket.init_app(self.app)
            self.login_manager.init_app(self.app)
            self.websocket.run(self.app, host=ip, port=port)
        except PermissionError:
            print_error(f'Failed to start team server on port {port}: Permission Denied.')
        except Exception:
            print_traceback()
