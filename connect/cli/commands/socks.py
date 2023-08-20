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
        socks_task = {
            'create': {
                'agent': current_agent,
                'method': self.name,
                'type': 2
            }
        }
        client_sio.emit('task', json.dumps(socks_task))
