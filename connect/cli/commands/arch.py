import json

from .commands import SystemInformationCommand


class Arch(SystemInformationCommand):
    def __init__(self):
        super().__init__(
            'arch',
            'Retrieve the architecture'
        )

    def execute_command(self, parameters, current_agent, client_sio):
        arch_task = {
            'create': {
                'agent': current_agent,
                'method': self.name,
                'type': 0,
                'module': self.module
            }
        }
        client_sio.emit('task', json.dumps(arch_task))
