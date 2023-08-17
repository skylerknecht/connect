import json
import textwrap

from connect.output import display
from .commands import BuiltinCommand


class Implant(BuiltinCommand):
    def __init__(self):
        super().__init__(
            'implants',
            'Create and list implants.',
            {
                'create': 'Create a new implant.',
                'list': 'List all implants.'
            }
        )

    def execute_command(self, parameters, client_sio):
        if len(parameters) < 1:
            client_sio.emit('implant', json.dumps({'list': None}))
            return
        switch = parameters[0]
        if switch == 'create':
            client_sio.emit('implant', json.dumps({'create': None}))
            return
        display(f'Invalid parameters: {" ".join(parameters)}', 'ERROR')

    @property
    def usage(self) -> str:
        return textwrap.dedent("""\
        usage:
            implants
            implants create
        """)
