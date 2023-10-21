import json
import textwrap
import re
from connect.output import display
from connect.cli.commands.commands import ConnectCommand

class Listeners(ConnectCommand):
    def __init__(self):
        super().__init__(
            'listeners',
            'Manage listeners.',
            parameters={
                'action': 'The action to perform (e.g., create, stop)',
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
            client_sio.emit('listener', {'list': None})
            return
        switch = parameters[0]
        if switch == 'create':
            if len(parameters) != 3:
                display(f'Expected <ip> <port> for create command', 'ERROR')
                return

            _, ip, port = parameters

            if not self.is_valid_ip(ip):
                display(f'{ip} is not a valid IP address', 'ERROR')
                return

            if not self.is_valid_port(port):
                display(f'{port} is not a valid port', 'ERROR')
                return

            listener_task = {
                'create': {
                    'ip': ip,
                    'port': int(port),
                }
            }
            client_sio.emit('listener', listener_task)
            return
        if switch == 'stop':
            if len(parameters) != 3:
                display(f'Expected <ip> <port> for stop command', 'ERROR')
                return

            _, ip, port = parameters

            if not self.is_valid_ip(ip):
                display(f'{ip} is not a valid IP address', 'ERROR')
                return

            if not self.is_valid_port(port):
                display(f'{port} is not a valid port', 'ERROR')
                return

            listener_task = {
                'stop': {
                    'ip': ip,
                    'port': int(port),
                }
            }
            client_sio.emit('listener', listener_task)
            return
        self.help()

    @property
    def usage(self) -> str:
        return textwrap.dedent("""\
        usage:
            listeners
            listeners create <ip> <port>
            listeners stop <ip> <port> 
        """)
