import textwrap
from connect.output import display
from connect.cli.commands.commands import ConnectCommand


class Implant(ConnectCommand):
    def __init__(self):
        super().__init__(
            'implants',
            'Create and list implants.',
            parameters={
                'action': 'The action to perform (e.g., create)',
            }
        )

    def execute_command(self, parameters, client_sio):
        if len(parameters) > 1:
            self.help()
            return
        if len(parameters) == 0:
            client_sio.emit('implant', {'list': None})
            return
        switch = parameters[0]
        if switch == 'create':
            client_sio.emit('implant', {'create': None})
            return
        display(f'Invalid parameters: {" ".join(parameters)}', 'ERROR')

    @property
    def usage(self) -> str:
        return textwrap.dedent("""\
        usage:
            implants
            implants create
        """)
