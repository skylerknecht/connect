import textwrap
from .commands import FileSystemCommand


class Type(FileSystemCommand):
    def __init__(self):
        super().__init__(
            'type',
            'Retrieve the contents of a file',
            parameters={
                'file': 'The path to the file you want to retrieve'
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
                    parameters[0]
                ]
            }
        }
        client_sio.emit('task', type_task)

    @property
    def usage(self) -> str:
        return textwrap.dedent("""\
        usage: 
            type <file>
        """)
