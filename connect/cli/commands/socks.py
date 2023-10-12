import json

from .commands import STDPapiAgentCommand


class Socks(STDPapiAgentCommand):
    def __init__(self):
        super().__init__(
            'socks',
            'Start a socks5 proxy.'
        )

    def execute_command(self, parameters, current_agent, client_sio):
        socks_task = {
            'create': {
                'agent': current_agent,
                'method': self.name,
                'type': 1,
            }
        }
        client_sio.emit('task', json.dumps(socks_task))
