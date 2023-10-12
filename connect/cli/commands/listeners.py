import json
import textwrap

from connect.output import display
from connect.cli.commands.commands import ConnectCommand


class Listeners(ConnectCommand):
    def __init__(self):
        super().__init__(
            'listeners',
            'Create and list listeners.',
            parameters={
                'create': 'Create a new listener.',
                'stop': 'Stop a listener.'
            }
        )

    def execute_command(self, parameters, client_sio):
        if len(parameters) < 1:
            client_sio.emit('listener', json.dumps({'list': None}))
            return
        switch = parameters[0]
        if switch == 'create':
            try:
                parameters[2] = int(parameters[2])
            except ValueError:
                display(f'Port must be an integer', 'ERROR')
                return
            if not (0 <= parameters[2] < 65535):
                display(f'Port must be between 0 and 65,535', 'ERROR')
                return
            listener_task = {
                'create': {
                    'ip': parameters[1],
                    'port': int(parameters[2]),
                }
            }
            client_sio.emit('listener', json.dumps(listener_task))
            return
        if switch == 'stop':
            try:
                parameters[2] = int(parameters[2])
            except ValueError:
                display(f'Port must be an integer', 'ERROR')
                return
            if not (0 <= parameters[2] < 65535):
                display(f'Port must be between 0 and 65,535', 'ERROR')
                return
            listener_task = {
                'stop': {
                    'ip': parameters[1],
                    'port': int(parameters[2]),
                }
            }
            client_sio.emit('listener', json.dumps(listener_task))
            return
        display(f'Invalid parameters: {" ".join(parameters)}', 'ERROR')

    @property
    def usage(self) -> str:
        return textwrap.dedent("""\
        usage:
            listeners
            listeners create 127.0.0.1 443
            listeners stop 127.0.0.1 443\
        """)
