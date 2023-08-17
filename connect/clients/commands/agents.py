import json
import textwrap

from .commands import BuiltinCommand
from connect.output import display


class Agent(BuiltinCommand):
    def __init__(self):
        super().__init__(
            'agents',
            'List agents.',
        )

    def execute_command(self, parameters, client_sio):
        if len(parameters) >= 1:
            display(f'The {self.name} command does not accept parameters', 'ERROR')
            return
        client_sio.emit('agent', json.dumps({'list': None}))