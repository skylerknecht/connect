import textwrap
import os
from .commands import FileSystemCommand
from connect.convert import xor_base64
from connect.output import display


class Upload(FileSystemCommand):
    def __init__(self):
        super().__init__(
            'upload',
            'Upload a file',
            parameters={
                'source': 'The path to the file you want to upload',
                'destination': 'The destination path where you want to upload the file',
            }
        )

    def execute_command(self, parameters, current_agent, client_sio):
        if len(parameters) != 2:
            self.help()
            return
        source_file = parameters[0]
        if not os.path.exists(source_file):
            display(f'{source_file} does not exist', 'ERROR')
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

    @property
    def usage(self) -> str:
        return textwrap.dedent("""\
        usage: 
            upload <source> <destination>
        """)
