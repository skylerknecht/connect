import json

from .commands import BuiltinAgentCommand


class Kill(BuiltinAgentCommand):
    def __init__(self):
        super().__init__(
            'kill',
            'Kills the agent'
        )

    def execute_command(self, parameters, current_agent, client_sio):
        kill_task = {
            'create': {
                'agent': current_agent,
                'method': self.name,
                'type': 1,
            }
        }
        client_sio.emit('task', json.dumps(kill_task))
