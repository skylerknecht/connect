import atexit
import os
import readline
import sys

from .commands import COMMANDS
from .commands.manager import CommandsManager
from .events import Events
from connect.output import display


class CLI:
    HISTORY_FILE = f'{os.getcwd()}/instance/.history'

    def __init__(self, name, prompt, commands):
        self.agents = []
        self.commands = commands | COMMANDS
        self.completer = Completer(self.commands.keys())
        self.PROMPT = prompt
        self.prompt = self.PROMPT
        self.arguments = None
        self.client_sio = Events(self.notify, self.set_cli_properties).sio
        self.commands_manager = CommandsManager(self.commands, self.client_sio)
        self.NAME = name

    def listen_for_user_input(self):
        print('Welcome to the Connect CLI, type help or ? to get started.')
        self.setup_readline()
        while True:
            try:
                user_input = input(self.prompt)
                if not user_input:
                    continue
                self.commands_manager.execute_command(user_input, self.set_cli_properties, self.get_cli_properties)
            except KeyboardInterrupt:
                # ToDo: do we need additional exceptions?
                # ToDo: is there a better way to handle this exception?
                print()  # This puts (connect)~#, the next prompt, on the next line.
                # CTRL+C kills the socketio connection, so we need to disconnect and reconnect.
                self.client_sio.disconnect()
                self.client_sio.connect(self.arguments.url, auth=self.arguments.key)
                continue

    def notify(self, *args):
        display('\033[1K\r', end='')
        display(*args)
        display(self.prompt + readline.get_line_buffer(), end='')
        sys.stdout.flush()

    def run(self, arguments):
        self.arguments = arguments
        if not arguments.no_server:
            self.client_sio.connect(arguments.url, auth=arguments.key)
        self.listen_for_user_input()

    def set_cli_properties(self, agents=None, prompt=None, reset: bool = False):
        if reset:
            self.prompt = self.PROMPT
            return
        self.prompt = prompt if prompt else self.prompt
        self.agents = agents if agents else self.agents
        if agents: self.completer.update_options(self.commands.keys() | [agent['id'] for agent in self.agents])

    def get_cli_properties(self, agent_ids=False):
        if agent_ids:
            return [agent['id'] for agent in self.agents]

    def retrieve_options(self):
        print(self.commands | [agent['id'] for agent in self.agents])
        return self.commands | [agent['id'] for agent in self.agents]

    def setup_readline(self):
        if not os.path.exists(self.HISTORY_FILE):
            with open(self.HISTORY_FILE, "w") as file:
                file.write("welcome to connect")
            display(f'Created command history file {self.HISTORY_FILE}', 'INFORMATION')
        try:
            readline.read_history_file(self.HISTORY_FILE)
            pass
        except Exception:
            display(f'Failed to open {self.HISTORY_FILE}', 'ERROR')
        readline.parse_and_bind('tab: complete')
        readline.set_completer(self.completer.complete_option)
        readline.set_completer_delims(" \t\n\"\\'`@$><=;|&{(")
        atexit.register(readline.write_history_file, self.HISTORY_FILE)


class Completer:
    def __init__(self, options):
        self.options = options

    def update_options(self, options):
        self.options = options

    def complete_option(self, incomplete_option, state):
        '''
            Analyzes the length of current line buffer / incomplete_option and
            determines the user(s) completion.

            If the current line buffer is greater or equal to one and the current line
            buffer ends with a trailing space then that indicates the user is attempting
            to complete a multi-worded option. The length of the current line buffer,
            when delimited by a space, must be incremented by one to correctly search
            for the next option.

            Otherwise, generate a list of all current menu options and file names that
            start with the current incomplete_option aka the last line in the buffer.

            Parameters:
                    incomplete_option (str()): The current incomplete option.
                    state (int()): An integer so that when the function is called
                                recursively by readline it can gather all items
                                within the current finished_option list.

            Returns:
                    finished_option (str): Whatever option the callee has not
                                        gathered yet.
            '''
        current_line = readline.get_line_buffer()
        current_line_list = current_line.split()
        if len(current_line_list) >= 1 and current_line.endswith(' '):
            current_line_list.append('')
        finished_options = [option for option in self.options if option.startswith(incomplete_option)]
        if '/' in incomplete_option:
            finished_options.extend(self._complete_path(incomplete_option))
        return finished_options[state]

    @staticmethod
    def _complete_path(incomplete_option):
        path = incomplete_option.split('/')
        incomplete_filename = path[-1]
        if len(path) == 1:
            return [filename for filename in os.listdir(f'/') if filename.startswith(incomplete_filename)]
        valid_path = '/'.join(path[:-1])
        return [
            f'{valid_path}/{filename}' if os.path.isfile(f'/{valid_path}/{filename}') else f'{valid_path}/{filename}/'
            for filename in os.listdir(f'/{valid_path}') if filename.startswith(incomplete_filename)]
