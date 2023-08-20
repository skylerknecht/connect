import json

from connect.cli.commands.commands import AgentCommand


class Whoami(AgentCommand):
    def __init__(self):
        super().__init__(
            'whoami',
            'Tasks the agent to retrieve the current username.'
        )

    def execute_command(self, parameters, current_agent, client_sio):
        whoami_task = {
            'create': {
                'agent': current_agent,
                'method': self.name,
                'type': 0
            }
        }
        client_sio.emit('task', json.dumps(whoami_task))
