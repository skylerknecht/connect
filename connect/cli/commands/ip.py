import json

from .commands import SystemInformationCommand


class IP(SystemInformationCommand):
    def __init__(self):
        super().__init__(
            'ip',
            'Retrieve the IP address'
        )

    def execute_command(self, parameters, current_agent, client_sio):
        ip_task = {
            'create': {
                'agent': current_agent,
                'method': self.name,
                'type': 1,
                'module': self.module
            }
        }
        client_sio.emit('task', ip_task)
