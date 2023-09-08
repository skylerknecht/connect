import json

from .commands import SystemInformationCommand


class Whoami(SystemInformationCommand):
    def __init__(self):
        super().__init__(
            'whoami',
            'Retrieve the current username.'
        )

    def execute_command(self, parameters, current_agent, client_sio):
        whoami_task = {
            'create': {
                'agent': current_agent,
                'method': self.name,
                'type': 0,
                'module': self.module
            }
        }
        client_sio.emit('task', json.dumps(whoami_task))