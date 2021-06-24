import re
import readline
import sys

from connect import color, engine, util

class CommandLine():

    banner = util.banner
    command_history = []
    menu_options = {}

    HISTORY_REGEX = re.compile(r'history\s\d')
    CONNECTION_REGEX = re.compile(r'\d')

    def __init__(self, prompt, connection=None):
        self.connection = connection
        self.prompt = prompt
        self.setup()

    def complete_command(self, incomplete_option, state):
        '''
        Analyzes the length of current line buffer / incomplete_option and
        determines the user(s) completion.

        If the current line buffer is greater or equal to one and the current line
        buffer ends with a trailing space then that indicates the user is attempting
        to complete a multi-optioned command. The length of the current line buffer,
        when delimeted by a space, must be incremented by one to correctly search
        for the next option.

        If the current line buffer is less than or equal to one then the user is
        attempting to complete a single-optioned command and should search the
        menu_options list for commands that starts with the current incomplete_option.

        If the current line buffer is greater than or equal to two and there is an
        option within the menu_options list that starts with the current line buffer
        then do the following:
            1. Retrieve all menu_options with the length greater than the length of
               the current line buffer.
            2. Identify the string within menu_options at the index of
               (current line buffer - 1) and identify which one starts with incomplete_option.

        Parameters:
                incomplete_option (str()): The current incomplete option.
                state (int()): An integer so that when the funciton is called
                               recursivley by readline it can gather all items
                               within the current finished_option list.
        Returns:
                finished_option (str): Whatever option the callee has not
                                       gathered yet.
        '''
        current_line = readline.get_line_buffer()
        current_line_list = current_line.split()
        if len(current_line_list) >= 1 and current_line.endswith(' '):
            current_line_list.append('')
        if len(current_line_list) <= 1:
            finished_option = [option for option in self.menu_options if option.startswith(incomplete_option)]
            return finished_option[state]
        if len(current_line_list) >= 2 and [option for option in self.menu_options if option.startswith(current_line)]:
            valid_options = [option for option in self.menu_options if len(option.split()) >= len(current_line_list)]
            finished_option = [option.split()[len(current_line_list) - 1] + ' ' for option in valid_options if option.split()[len(current_line_list) - 1].startswith(incomplete_option)]
            return finished_option[state]
        return 0

    def display_command_history(self):
        color.display_banner('Command History')
        for number, command in enumerate(self.command_history):
            color.normal(f'{number} : {command}')
        color.normal('')
        return 0

    def display_connection_information(self):
        color.normal(self.connection)
        return 0

    def display_banner(self):
        color.normal(self.banner)
        return 0

    def exit(self):
        return -1

    def help_menu(self):
        color.display_banner('Help Menu')
        for option, option_description in self.menu_options.items():
            if option_description[1]:
                color.normal(f'\'{option}\': {option_description[1]}')
        color.normal('')
        return 0

    def process_user_input(self, user_input):
        try:
            if self.HISTORY_REGEX.match(user_input):
                user_input = self.command_history[int(user_input.split(" ")[1])]
            return self.menu_options[user_input][0]()
        except KeyError:
            color.error('Invalid command.')
            return 1

    def setup(self):
        self.setup_menu()
        self.setup_readline()
        if self.connection:
            self.setup_connection_menu()
        else:
            self.update_connection_options()

    def setup_basics(self):
        self.menu_options['?'] = (self.help_menu, 'Displays the help menu.')
        self.menu_options['exit'] = (self.exit, 'Exits the current command-line.')
        self.menu_options['help'] = (self.help_menu, 'Displays the help menu.')
        self.menu_options['history'] = (self.display_command_history, 'Displays the command history. Execute a previous command by appending an index (e.g., history 0)')
        self.menu_options['version'] = (self.version, 'Display the current application version.')

    def setup_connection_menu(self):
        self.menu_options = {}
        self.setup_basics()
        self.menu_options['connection information'] = (self.display_connection_information, 'Display current connection information.')
        self.menu_options.update(self.connection.menu_options)

    def setup_menu(self):
        self.setup_basics()
        self.menu_options['connections'] = (util.engine.display_connections, 'Displays current connections.')
        self.menu_options['implants'] = (util.engine.display_implants, 'Displays hosted implants ready for delivery.')

    def setup_readline(self):
        readline.parse_and_bind('tab: complete')
        readline.set_completer(self.complete_command)
        readline.set_completer_delims(" \t\n\"\\'`@$><=;|&{(")

    def update_connection_options(self):
        for connection_id, connection in util.engine.connections.items():
            if connection.status == 'connected':
                self.menu_options[connection_id] = (connection.interact, None)

    def version(self):
        color.normal(util.__version__)
        return 0

    def run(self):
        while True:
            try:
                self.setup()
                user_input = color.display_prompt(self.prompt, connection=self.connection).lower()
                if not user_input:
                    continue
                return_code = self.process_user_input(user_input)
                if return_code != 1 and user_input not in self.command_history:
                    self.command_history.append(user_input)
                if return_code < 0:
                    break
            except (EOFError, KeyboardInterrupt) as e:
                user_input = color.information('Are you sure you want to quit? [yes/no]:', user_input=True)
                if user_input == 'yes':
                    break
                continue
