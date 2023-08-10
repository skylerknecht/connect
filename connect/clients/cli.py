import argparse

from .commands import commands_manager
from .events import sio


class CLI:
    NAME = 'cli'
    PROMPT = '(connect)~# '

    def __init__(self):
        self.arguments = None
        self.prompt = self.PROMPT

    def listen_for_user_input(self):
        print('Welcome to the Connect CLI, type help or ? to get started.')
        while True:
            try:
                user_input = input(self.prompt)
                if not user_input:
                    continue
                commands_manager.execute_command(user_input, self.set_cli_properties)
            except KeyboardInterrupt:
                # ToDo: do we need additional exceptions?
                # ToDo: is there a better way to handle this exception?
                print()
                continue

    def run(self, arguments):
        self.arguments = arguments
        if not arguments.no_server:
            sio.connect(arguments.url, auth=arguments.key)
        self.listen_for_user_input()

    def set_cli_properties(self, prompt=None):
        self.prompt = prompt if prompt else None

    def setup_parser(self, subparser):
        parser = subparser.add_parser(self.NAME, help='Command Line Interface (CLI) for interacting with the '
                                                      'team server.',
                                      formatter_class=argparse.RawTextHelpFormatter, usage=argparse.SUPPRESS)
        parser.add_argument('url', metavar='url', help='Team Server URL.', default='127.0.0.1')
        parser.add_argument('key', metavar='key', help='Team Server Key.', default='8080')
        parser.add_argument('--no-server', action='store_true', help='Don\'t connect to the team server.')
