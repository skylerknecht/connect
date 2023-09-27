import json
import textwrap

from connect.output import display
from connect.cli.commands.commands import STDPAPICommand


class Listeners(STDPAPICommand):
    def __init__(self):
        super().__init__(
            'listeners',
            'Create and list listeners.',
            parameters={
                'create': 'Create a new listener.',
            }
        )

    def execute_command(self, parameters, client_sio):
        if len(parameters) < 1:
            client_sio.emit('listener', json.dumps({'list': None}))
            return
        try:
            parameters[2] = int(parameters[2])
        except ValueError:
            display(f'Port must be an integer', 'ERROR')
            return
        if not (0 <= parameters[2] < 65535):
            display(f'Port must be between 0 and 65,535', 'ERROR')
            return
        switch = parameters[0]
        if switch == 'create':
            listener = {
                'create': {
                    'ip': parameters[1],
                    'port': int(parameters[2]),
                }
            }
            client_sio.emit('listener', json.dumps(listener))
            return
        display(f'Invalid parameters: {" ".join(parameters)}', 'ERROR')

    @property
    def usage(self) -> str:
        return textwrap.dedent("""\
        usage:
            listeners
            listeners create
        """)
