import json

from .commands import BuiltinCommand
from ..events import sio


class Implant(BuiltinCommand):
    def __init__(self):
        super().__init__(
            'implant',
            'Create and list implants with implant [create|list].',
            {
                'create': 'Create a new implant.',
                'list': 'List all implants.'
            }
        )

    def execute_command(self, parameters):
        switch = parameters[0]
        if switch == 'create':
            sio.emit('implant', json.dumps({'action': 'create'}))
