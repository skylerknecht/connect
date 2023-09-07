import sys

from .commands import STDPAPICommand


class Exit(STDPAPICommand):
    def __init__(self):
        super().__init__(
            'exit',
            'Exits the CLI.'
        )

    def execute_command(self, parameters, client_sio):
        client_sio.disconnect()
        sys.exit()
