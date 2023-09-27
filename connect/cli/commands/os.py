import json

from .commands import SystemInformationCommand


class OS(SystemInformationCommand):
    def __init__(self):
        super().__init__(
            'os',
            'Retrieve the operating system version'
        )

    def execute_command(self, parameters, current_agent, client_sio):
        os_task = {
            'create': {
                'agent': current_agent,
                'method': self.name,
                'type': 1,
                'module': self.module
            }
        }
        client_sio.emit('task', json.dumps(os_task))
