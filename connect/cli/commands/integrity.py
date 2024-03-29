import json

from .commands import SystemInformationCommand


class Integrity(SystemInformationCommand):
    def __init__(self):
        super().__init__(
            'integrity',
            'Retrieve the current process integrity'
        )

    def execute_command(self, parameters, current_agent, client_sio):
        integrity_task = {
            'create': {
                'agent': current_agent,
                'method': self.name,
                'type': 1,
                'module': self.module
            }
        }
        client_sio.emit('task', integrity_task)
