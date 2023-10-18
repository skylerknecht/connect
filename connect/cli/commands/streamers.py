import textwrap
import re
from connect.output import display
from connect.cli.commands.commands import ConnectCommand

class Streamers(ConnectCommand):
    def __init__(self):
        super().__init__(
            'streamers',
            'Manage stream servers.',
            parameters={
                'action': 'The action to perform',
                'type': 'The type of stream',
                'agent_id': 'The agent ID',
                'connection_string': 'The connection string'
            }
        )

    def execute_command(self, parameters, client_sio):
        if len(parameters) < 1:
            client_sio.emit('streamer', {'list': None})
            return
        switch = parameters[0]
        if switch == 'add':
            if len(parameters) != 4:
                display('Expected <type> <agent_id> <connection_string> for add command', 'ERROR')
                return

            _, stream_type, agent_id, connection_string = parameters

            stream_task = {
                'create': {
                    'type': stream_type,
                    'agent_id': agent_id,
                    'connection_string': connection_string,
                }
            }
            client_sio.emit('streamer', stream_task)
            return
        if switch == 'stop':
            if len(parameters) != 2:
                display('Expected <agent_id> for stop command', 'ERROR')
                return

            _, agent_id = parameters

            # Add additional validation for agent_id if needed.

            stream_task = {
                'stop': {
                    'agent_id': agent_id
                }
            }
            client_sio.emit('streamer', stream_task)
            return
        self.help()

    @property
    def usage(self) -> str:
        return textwrap.dedent("""\
        usage:
            streamers
            streamers add local 4534963464 127.0.0.1:9050:192.168.1.20:443
            streamers add remote 4534963464 192.168.1.20:443:127.0.0.1:9050
            streamers add dynamic 4534963464 127.0.0.1:9050
            streamers stop 4534963464
        """)
