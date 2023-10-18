import json

from .commands import ProcessesCommand


class PS(ProcessesCommand):
    def __init__(self):
        super().__init__(
            'ps',
            'Retrieve the current processes'
        )

    def execute_command(self, parameters, current_agent, client_sio):
        ps_task = {
            'create': {
                'agent': current_agent,
                'method': self.name,
                'type': 1,
                'module': self.module
            }
        }
        client_sio.emit('task', ps_task)
