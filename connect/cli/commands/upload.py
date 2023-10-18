import json

from .commands import FileSystemCommand
from connect.convert import string_to_base64, xor_base64


class Upload(FileSystemCommand):
    def __init__(self):
        super().__init__(
            'upload',
            'Upload a file',
            parameters={
                'source': 'What file should we upload',
                'destination': 'Where should we upload the file',
            }
        )

    def execute_command(self, parameters, current_agent, client_sio):
        if len(parameters) != 2:
            self.help()
            return
        base64_file_to_upload, key = xor_base64(open(parameters[0], 'rb').read())
        upload_task = {
            'create': {
                'agent': current_agent,
                'method': self.name,
                'type': 1,
                'module': self.module,
                'parameters': [
                    base64_file_to_upload,
                    key,
                    parameters[1]
                ]
            }
        }
        client_sio.emit('task', upload_task)
