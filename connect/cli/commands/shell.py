import textwrap

from .commands import ExecutionCommand


class Shell(ExecutionCommand):
    def __init__(self):
        super().__init__(
            'shell',
            'Execute a command',
            parameters={
                'command': 'The command to execute (e.g., whoami)'
            }
        )

    def execute_command(self, parameters, current_agent, client_sio):
        if not parameters:
            self.help()
            return
        shell_task = {
            'create': {
                'agent': current_agent,
                'method': self.name,
                'type': 1,
                'module': self.module,
                'parameters': [
                    *parameters
                ]
            }
        }
        client_sio.emit('task', shell_task)

    @property
    def usage(self) -> str:
        return textwrap.dedent("""\
        usage: 
            shell <command>
        """)
