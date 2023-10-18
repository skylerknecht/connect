import json

from .commands import STDPapiAgentCommand


class Interactive(STDPapiAgentCommand):
    def __init__(self):
        super().__init__(
            'interactive',
            'Enable interactive mode'
        )

    def execute_command(self, parameters, current_agent, client_sio):
        interactive_task = {
            'create': {
                'agent': current_agent,
                'method': self.name,
                'type': 0,
            }
        }
        client_sio.emit('task', interactive_task)
