import json

from .commands import SystemInformationCommand


class PWD(SystemInformationCommand):
    def __init__(self):
        super().__init__(
            'pwd',
            'Retrieve the current working directory'
        )

    def execute_command(self, parameters, current_agent, client_sio):
        pwd_task = {
            'create': {
                'agent': current_agent,
                'method': self.name,
                'type': 0,
                'module': self.module
            }
        }
        client_sio.emit('task', json.dumps(pwd_task))
