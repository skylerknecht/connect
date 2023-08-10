import sys

from .commands import BuiltinCommand
from ..events import sio


class Exit(BuiltinCommand):
    def __init__(self):
        super().__init__('exit', 'Exits the CLI.', {})

    def execute_command(self, parameters):
        sio.disconnect()
        sys.exit()
