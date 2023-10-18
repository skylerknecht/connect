import json

from .commands import FileSystemCommand
from connect.convert import string_to_base64


class Type(FileSystemCommand):
    def __init__(self):
        super().__init__(
            'type',
            'Retrieve the contents of a file',
            parameters={
                'file': 'What file contents should we retrieve'
            }
        )

    def execute_command(self, parameters, current_agent, client_sio):
        if len(parameters) != 1:
            self.help()
            return
        type_task = {
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
        client_sio.emit('task', type_task)
