import json

from .commands import ExecutionCommand
from connect.convert import string_to_base64


class Shell(ExecutionCommand):
    def __init__(self):
        super().__init__(
            'shell',
            'Execute a command',
            parameters={
                'command': 'What command should we execute'
            }
        )

    def execute_command(self, parameters, current_agent, client_sio):
        if not parameters:
            self.help()
            return
        shell_arguments = []
        for parameter in parameters:
            shell_arguments.append(string_to_base64(parameter))
        shell_task = {
            'create': {
                'agent': current_agent,
                'method': self.name,
                'type': 0,
                'module': self.module,
                'parameters': [
                    *shell_arguments
                ]
            }
        }
        client_sio.emit('task', json.dumps(shell_task))
