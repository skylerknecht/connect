import argparse
import readline

from .commands import COMMANDS
from .commands.commands import CommandsManager
from connect.output import display
from .events import Events


class CLI:
    NAME = 'cli'
    PROMPT = '(connect)~# '

    def __init__(self):
        self.arguments = None
        self.client_sio = Events(self.notify).sio
        self.commands_manager = CommandsManager(COMMANDS, self.client_sio)
        self.prompt = self.PROMPT

    def listen_for_user_input(self):
        print('Welcome to the Connect CLI, type help or ? to get started.')
        while True:
            try:
                user_input = input(self.prompt)
                if not user_input:
                    continue
                self.commands_manager.execute_command(user_input, self.set_cli_properties)
            except KeyboardInterrupt:
                # ToDo: do we need additional exceptions?
                # ToDo: is there a better way to handle this exception?
                print()  # This puts (connect)~#, the next prompt, on the next line.
                # CTRL+C kills the socketio connection, so we need to disconnect and reconnect.
                self.client_sio.disconnect()
                self.client_sio.connect(self.arguments.url, auth=self.arguments.key)
                continue

    def notify(self, *args):
        """
        Asynchronous requests to stdout may cause issues with terminal output. We proxy all of these
        requests through this function to prevent this from happening. When an operator executes a
        command a new prompt will display prior to the results being received. We'll first remove this
        prompt with `\033[1k\r` and then print the results. Secondly, the stdin will be holding all stdout
        until a carriage return is provided. To provide a new prompt and statisfy stdin we'll prefix the prompt
        with a carriage return. Finally, to prevent the cursor from starting on the next line we'll instruct
        print to not add a carriage return to the suffix of stdout.
        """
        display('\033[1K\r', end='')
        display(*args)
        display(f'\r{self.prompt}{readline.get_line_buffer()}', end='')

    def run(self, arguments):
        self.arguments = arguments
        if not arguments.no_server:
            self.client_sio.connect(arguments.url, auth=arguments.key)
        self.listen_for_user_input()

    def set_cli_properties(self, prompt=None, reset: bool = False):
        if reset:
            self.prompt = self.PROMPT
            return
        self.prompt = prompt if prompt else None

    def setup_parser(self, subparser):
        parser = subparser.add_parser(self.NAME, help='Command Line Interface (CLI) for interacting with the '
                                                      'team server.',
                                      formatter_class=argparse.RawTextHelpFormatter, usage=argparse.SUPPRESS)
        parser.add_argument('key', metavar='key', help='Team Server Key.', default='8080')
        parser.add_argument('--url', metavar='url', help='Team Server URL.', default='http://127.0.0.1:1337/')
        parser.add_argument('--no-server', action='store_true', help='Don\'t connect to the team server.')
