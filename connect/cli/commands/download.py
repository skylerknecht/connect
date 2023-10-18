import textwrap
from .commands import FileSystemCommand


class Download(FileSystemCommand):
    def __init__(self):
        super().__init__(
            'download',
            'Download a file',
            parameters={
                'source': 'The file to download'
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

    @property
    def usage(self) -> str:
        return textwrap.dedent("""\
        usage:
            download <source>
        """)
