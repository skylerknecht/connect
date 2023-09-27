import json

from .commands import FileSystemCommand
from connect.convert import string_to_base64


class Dir(FileSystemCommand):
    def __init__(self):
        super().__init__(
            'dir',
            'Retrieve the contents of a directory',
            parameters={
                'directory': 'What directory contents should we retrieve'
            }
        )

    def execute_command(self, parameters, current_agent, client_sio):
        if len(parameters) != 1:
            self.help()
            return
        dir_task = {
            'create': {
                'agent': current_agent,
                'method': self.name,
                'type': 1,
                'module': self.module,
                'parameters': [
                    string_to_base64(parameters[0])
                ]
            }
        }
        client_sio.emit('task', json.dumps(dir_task))
