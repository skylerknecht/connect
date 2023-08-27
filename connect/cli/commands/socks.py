import json
import textwrap

from connect.output import display
from connect.cli.commands.commands import AgentCommand


class Socks(AgentCommand):
    def __init__(self):
        super().__init__(
            'socks',
            'Create a socks proxy to an agent.'
        )

    def execute_command(self, parameters, current_agent, client_sio):
        if len(parameters) != 1:
            display('Please provide a port', 'ERROR')
            return
        try:
            port = int(parameters[0])
        except ValueError:
            display(f'{parameters[0]} is not an integer', 'ERROR')
            return
        socks_task = {
            'create': {
                'agent': current_agent,
                'method': self.name,
                'misc': [str(port)],
                'type': 2
            }
        }
        client_sio.emit('task', json.dumps(socks_task))
