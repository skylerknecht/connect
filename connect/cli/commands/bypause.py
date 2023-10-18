import json

from .commands import MiscAgentCommand


class ByPause(MiscAgentCommand):
    def __init__(self):
        super().__init__(
            'bypause',
            'Retrieve the current username.'
        )

    def execute_command(self, parameters, current_agent, client_sio):
        bypause_task = {
            'create': {
                'agent': current_agent,
                'method': self.name,
                'type': 1,
                'module': f'{self.MODULE_PATH}/Bypause.dll'
            }
        }
        client_sio.emit('task', bypause_task)
