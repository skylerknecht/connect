import json
import os

from .commands import ExecutionCommand
from connect.convert import string_to_base64, xor_base64
from connect.output import display


class ExecuteAssembly(ExecutionCommand):
    def __init__(self):
        super().__init__(
            'execute-assembly',
            'Execute a .NET assembly',
            parameters={
                'command': 'What assembly should we execute',
                'arguments': 'What arguments should we send to the assembly'
            }
        )

    def execute_command(self, parameters, current_agent, client_sio):
        if not parameters:
            self.help()
            return
        if not os.path.exists(parameters[0]):
            display(f'{parameters[0]} does not exist.', 'ERROR')
            return
        base64_assembly_to_execute, key = xor_base64(open(parameters[0], 'rb').read())
        assembly_arguments = []
        for parameter in parameters[1:]:
            assembly_arguments.append(string_to_base64(parameter))
        shell_task = {
            'create': {
                'agent': current_agent,
                'method': self.name,
                'type': 1,
                'module': self.module,
                'parameters': [
                    base64_assembly_to_execute,
                    key,
                    *assembly_arguments
                ]
            }
        }
        client_sio.emit('task', shell_task)