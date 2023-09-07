import json

from .commands import FileSystemCommand


class Drives(FileSystemCommand):
    def __init__(self):
        super().__init__(
            'drives',
            'Retrieve available drives'
        )

    def execute_command(self, parameters, current_agent, client_sio):
        drives_task = {
            'create': {
                'agent': current_agent,
                'method': self.name,
                'type': 0,
                'module': self.module,
            }
        }
        client_sio.emit('task', json.dumps(drives_task))
