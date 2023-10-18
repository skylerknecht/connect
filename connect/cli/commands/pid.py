import json

from .commands import SystemInformationCommand


class PID(SystemInformationCommand):
    def __init__(self):
        super().__init__(
            'pid',
            'Retrieve the current process identifier'
        )

    def execute_command(self, parameters, current_agent, client_sio):
        pid_task = {
            'create': {
                'agent': current_agent,
                'method': self.name,
                'type': 1,
                'module': self.module
            }
        }
        client_sio.emit('task', pid_task)
