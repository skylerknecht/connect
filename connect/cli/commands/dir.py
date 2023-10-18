import textwrap
from .commands import FileSystemCommand


class Dir(FileSystemCommand):
    def __init__(self):
        super().__init__(
            'dir',
            'Retrieve the contents of a directory',
            parameters={
                'directory': 'The path to the directory whose contents you want to retrieve'
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
                    parameters[0]
                ]
            }
        }
        client_sio.emit('task', dir_task)

    @property
    def usage(self) -> str:
        return textwrap.dedent("""\
        usage: 
            dir <directory>
        """)
