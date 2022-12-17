from connect.output import print_error

from flask import Flask


class HTTPListener(object):
    """
    A WebSocket Flask App Wrapper.
    """

    team_server_uri = ''
    team_server_key = ''

    def __init__(self, name, config, db, websocket):
        self.app = Flask(name)
        self.app.config.from_object(config)
        self.websocket = websocket
        self.db = db

    def add_event(self, message, handler):
        self.websocket.on(message, handler)

    def add_blueprint(self, blueprint):
        self.app.register_blueprint(blueprint)

    def connect(self):
        try:
            self.websocket.connect(self.team_server_uri, auth=self.team_server_key)
        except Exception:
            print_error(f'HTTP listener could not connect to {self.team_server_uri}')

    def run(self, ip, port):
        self.connect()
        try:
            self.db.init_app(self.app)
            self.app.run(host=ip, port=port)
        except Exception:
            print_error(f'Failed ot start HTTP listener on http://{ip}:{port}/')

