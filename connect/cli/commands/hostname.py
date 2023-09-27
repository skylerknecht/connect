import json

from .commands import SystemInformationCommand


class Hostname(SystemInformationCommand):
    def __init__(self):
        super().__init__(
            'hostname',
            'Retrieve the hostname'
        )

    def execute_command(self, parameters, current_agent, client_sio):
        hostname_task = {
            'create': {
                'agent': current_agent,
                'method': self.name,
                'type': 1,
                'module': self.module
            }
        }
        client_sio.emit('task', json.dumps(hostname_task))
