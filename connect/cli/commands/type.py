import json

from .commands import FileSystemCommand


class Type(FileSystemCommand):
    def __init__(self):
        super().__init__(
            'type',
            'Retrieve the contents of a file'
        )

    def execute_command(self, parameters, current_agent, client_sio):
        type_task = {
            'create': {
                'agent': current_agent,
                'method': self.name,
                'type': 0,
                'module': self.module,
            }
        }
        client_sio.emit('task', json.dumps(type_task))
