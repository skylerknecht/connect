from connect.output import display
from connect.server.flask_server import FlaskServerBase
from connect.server.tasks import TaskManager
from . import views


class HTTPListener(FlaskServerBase):
    def __init__(self):
        self.NAME = 'http_listener'
        super().__init__()

    def run(self, arguments):
        self.setup_app()
        task_manager = TaskManager()
        views.HTTPListenerRoutes(self.app, task_manager)
        try:
            # if arguments:
            #     events.socketio.run(self.app, host=ip, port=port, keyfile=keyfile, certfile=certfile)
            #     return
            display(f'Starting {self.NAME} on {arguments.ip}:{arguments.port}', 'INFORMATION')
            self.app.run(host=arguments.ip, port=arguments.port)
        except PermissionError:
            display(f'Failed to start {self.NAME} on port {arguments.port}: Permission Denied.', 'ERROR')