import os
import re
import readline

from collections import namedtuple
from shlex import split

class Messages:

    Message = namedtuple('Message', ['color', 'symbol'])
    debug = 0

    COLORS = {
        'cyan':'\001\033[0;36m\002',
        'green':'\001\033[0;32m\002',
        'red':'\001\033[0;31m\002',
        'default':'\001\033[0;0m\002',
        'yellow':'\001\033[0;33m\002',
    }

    def __init__(self, messages={}):
        self.messages = {
            'default': self.Message(self.COLORS['default'], ''),
            'error': self.Message(self.COLORS['red'], '[-] '),
            'information': self.Message(self.COLORS['yellow'], '[!] '),
            'prompt': self.Message(self.COLORS['cyan'], ''),
            'success': self.Message(self.COLORS['green'], '[+] '),
        }
        self.messages.update(messages)

    def header(self, text):
        self.print('default', '')
        self.print('default', f'{text}')
        self.print('default', '='*len(text))
        self.print('default', '')

    def print(self, type, text, end='\n'):
        message = self.messages[type]
        output = f'\001\033[0;0m\002{message.color}{message.symbol}{text}\001\033[0;0m\002'
        if type == 'prompt':
            return input(f'{output} ')
        print(output, end=end)

    def verbose(self, text, level):
        if level > self.debug:
            return
        self.print('information', text)

class CommandLine(Messages):

    MenuOption = namedtuple('MenuOption', ['function', 'description', 'category', 'message_type', 'arguments'])
    __version__ = '0.0'

    def __init__(self, prompt, messages={}):
        super().__init__(messages=messages)
        self.menu_options = {}
        self.prompt = prompt
        self.setup_menu()

    def _complete_path(self, incomplete_option):
        path = incomplete_option.split('/')
        incomplete_filename = path[-1]
        if len(path) == 1:
            return [filename for filename in os.listdir(f'/') if filename.startswith(incomplete_filename)]
        valid_path = '/'.join(path[:-1])
        return [f'{valid_path}/{filename}' if os.path.isfile(f'/{valid_path}/{filename}') else f'{valid_path}/{filename}/' for filename in os.listdir(f'/{valid_path}') if filename.startswith(incomplete_filename)]

    def complete_option(self, incomplete_option, state):
        '''
        Analyzes the length of current line buffer / incomplete_option and
        determines the user(s) completion.

        If the current line buffer is greater or equal to one and the current line
        buffer ends with a trailing space then that indicates the user is attempting
        to complete a multi-worded option. The length of the current line buffer,
        when delimeted by a space, must be incremented by one to correctly search
        for the next option.

        Otherwise, generate a list of all current menu options and file names that
        start with the current incomplete_option aka the last line in the buffer.

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
        finished_options = [option for option in self.menu_options if option.startswith(incomplete_option)]
        if '/' in incomplete_option:
            finished_options.extend(self._complete_path(incomplete_option))
        return finished_options[state]

    def exit(self):
        return -3, 'User exit'

    def help_menu(self):
        categories = []
        for option, option_values in self.menu_options.items():
            if option_values.category == 'NOP-tions':
                continue
            if not option_values.category in categories:
                categories.append(option_values.category)
        for category in categories:
            self.header(category)
            for option, option_values in self.menu_options.items():
                if option_values.category == category:
                    self.print(option_values.message_type, f'\'{str(option)}\': {option_values.description}')
        self.print('default', '')
        return 0, 'Success'

    def process_user_input(self, user_input):
        try:
            user_input = split(user_input)
            option = self.menu_options[user_input[0].lower()]
            if option.arguments:
                return option.function(user_input)
            return option.function()
        except KeyError as ke:
            return -1, f'Invalid option: {ke}.'
        except ValueError as ve:
            return -1, f'Invalid value: {ve}'
        except IndexError as ie:
            return -1, f'Arguments expected.'
        except Exception as e:
            return -2, f'Unknown error occured: {e}'

    def setup_menu(self):
        self.update_options('?', self.help_menu, 'Displays the help menu.', 'Options')
        self.update_options('exit', self.exit, 'Exits the current command line.', 'Options')
        self.update_options('help', self.help_menu, 'Displays the help menu.', 'Options')
        self.update_options('verbosity', self.verbosity, 'Set the verbosity level (i.e., verbosity 1)', 'Options', arguments=True)
        self.update_options('version', self.version, 'Display the current application version.', 'Options')

    def setup_readline(self):
        readline.parse_and_bind('tab: complete')
        readline.set_completer(self.complete_option)
        readline.set_completer_delims(" \t\n\"\\'`@$><=;|&{(")

    def update_options(self, name, function, description, category, message_type='default', arguments=False):
        self.menu_options[name] = self.MenuOption(function, description, category, message_type, arguments)

    def verbosity(self, input):
        level = int(input[1])
        if level > 3:
            return -1, 'Excpected a level from zero to three (i.e., verbosity 1).'
        self.print('information', f'Setting verbosity level to {level}')
        self.debug = level
        return 0, 'Success'

    def version(self):
        self.print('default', self.__version__)
        return 0, 'Success'

    def run(self):
        while True:
            try:
                self.setup_readline() # Hackey-ish way to setup readline :/
                user_input = self.print('prompt', self.prompt)
                if not user_input:
                    continue
                return_code, text = self.process_user_input(user_input)
                if return_code == 0:
                    continue
                if return_code == -1:
                    self.print('information', text)
                    continue
                if return_code == -2:
                    self.print('error', text)
                    continue
                if return_code == -3:
                    break
            except (EOFError, KeyboardInterrupt) as e:
                self.print('default', '')
                continue
