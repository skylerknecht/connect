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
                'action': 'The action to perform (e.g., add, stop)',
                'type': 'The type of stream (e.g., dynamic)',
                'agent_id': 'The agent ID',
                'ip': 'The IP address to bind to (e.g., 127.0.0.1)',
                'port': 'The port to bind to (e.g., 443)',
            }
        )

    @staticmethod
    def is_valid_ip(ip):
        # Regular expression to validate an IP address
        ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
        return bool(re.match(ip_pattern, ip))

    @staticmethod
    def is_valid_port(port):
        try:
            port_num = int(port)
            return 0 <= port_num <= 65535  # Ports should be in the range [0, 65535]
        except ValueError:
            return False

    def execute_command(self, parameters, client_sio):
        if len(parameters) < 1:
            client_sio.emit('streamer', {'list': None})
            return
        switch = parameters[0]
        if switch == 'add':
            if len(parameters) != 5:
                display(f'Excepted <type> <agent_id> <ip> <port> for add command', 'ERROR')
                return

            _, stream_type, agent_id, ip, port = parameters

            if not self.is_valid_ip(ip):
                display(f'{ip} is not a valid IP address', 'ERROR')
                return

            if not self.is_valid_port(port):
                display(f'{port} is not a valid port ', 'ERROR')
                return

            stream_task = {
                'create': {
                    'type': stream_type,
                    'agent_id': agent_id,
                    'ip': ip,
                    'port': int(port),
                }
            }
            client_sio.emit('streamer', stream_task)
            return
        if switch == 'stop':
            if len(parameters) != 2:
                display(f'Excepted <agent_id> for add command.', 'ERROR')
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
            streamers add <type> <agent_id> <ip> <port>
            streamers stop <agent_id>
        """)
