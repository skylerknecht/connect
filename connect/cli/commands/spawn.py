import textwrap
from .commands import MiscAgentCommand


class Spawn(MiscAgentCommand):
    def __init__(self):
        super().__init__(
            'spawn',
            'Spawn a new agent',
            parameters={
                'uri': 'The listener URI to connect to',
                'key': 'The implant key to use',
            }
        )

    def execute_command(self, parameters, current_agent, client_sio):
        if len(parameters) != 2:
            self.help()
            return
        upload_task = {
            'create': {
                'agent': current_agent,
                'method': self.name,
                'type': 1,
                'module': f'{self.MODULE_PATH}/Spawn.dll',
                'parameters': [
                    parameters[0],
                    parameters[1]
                ]
            }
        }
        client_sio.emit('task', upload_task)

    @property
    def usage(self) -> str:
        return textwrap.dedent("""\
        usage: 
            spawn <uri> <key>
        """)
