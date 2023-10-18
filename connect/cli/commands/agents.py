import json

from connect.cli.commands.commands import ConnectCommand
from connect.output import display


class Agent(ConnectCommand):
    def __init__(self):
        super().__init__(
            'agents',
            'List agents.',
            parameters={
                'seconds': 'What should the maximum check in time be'
            }
        )

    def execute_command(self, parameters, client_sio):
        if len(parameters) > 1:
            self.help()
            return
        try:
            seconds = int(parameters[0]) if len(parameters) == 1 else 60
        except ValueError:
            display('Seconds must be an integer', 'ERROR')
            return
        client_sio.emit('agent', {'list': {'seconds': seconds}})
