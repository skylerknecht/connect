import json

from .commands import FileSystemCommand


class PWD(FileSystemCommand):
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
                'type': 1,
                'module': self.module
            }
        }
        client_sio.emit('task', pwd_task)
