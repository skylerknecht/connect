import re
import readline

from connect import color, util

class CommandLine():

    def __init__(self, prompt, connection=None):
        self.connection = connection
        self.menu_options = {}
        self.prompt = prompt
        self.setup_menu()

    def complete_option(self, incomplete_option, state):
        '''
        Analyzes the length of current line buffer / incomplete_option and
        determines the user(s) completion.

        If the current line buffer is greater or equal to one and the current line
        buffer ends with a trailing space then that indicates the user is attempting
        to complete a multi-worded option. The length of the current line buffer,
        when delimeted by a space, must be incremented by one to correctly search
        for the next option.

        If the current line buffer is less than or equal to one then the user is
        attempting to complete a single-worded option and should search the
        menu_options list for options that starts with the current incomplete_option.

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
        return 0, 'Success'

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
            color.header(category)
            for option, option_values in self.menu_options.items():
                if option_values.category == category:
                    option_values.color(f'\'{str(option)}\': {option_values.description}')
        color.normal('')
        return 0, 'Success'

    def process_user_input(self, user_input):
        try:
            user_input = re.split(r'(?<!\\)\s', user_input)
            option = self.menu_options[user_input[0].lower()]
            if option.arguments:
                return option.function(user_input)
            return option.function()
        except KeyError:
            return -1, 'Invalid option.'

    def setup_menu(self):
        self.menu_options['?'] = util.MenuOption(self.help_menu, 'Displays the help menu.', 'Options', color.normal, False)
        self.menu_options['exit'] = util.MenuOption(self.exit, 'Exits the current command line.', 'Options', color.normal, False)
        self.menu_options['help'] = util.MenuOption(self.help_menu, 'Displays the help menu.', 'Options', color.normal, False)
        self.menu_options['verbosity'] = util.MenuOption(self.verbosity, 'Toggle verbosity mode on and off.', 'Options', color.normal, False)
        self.menu_options['version'] = util.MenuOption(self.version, 'Display the current application version.', 'Options', color.normal, False)

    def setup_readline(self):
        readline.parse_and_bind('tab: complete')
        readline.set_completer(self.complete_option)
        readline.set_completer_delims(" \t\n\"\\'`@$><=;|&{(")

    def update_options(self, options):
        self.menu_options.update(options)

    def verbosity(self):
        color.information(f'Setting verbosity to {not util.verbose}')
        util.verbose = not util.verbose
        return 0, 'Success'

    def version(self):
        color.normal(util.__version__)
        return 0, 'Success'

    def run(self):
        while True:
            try:
                self.setup_readline() # Hackey-ish way to setup readline :/
                user_input = color.prompt(self.prompt)
                if not user_input:
                    continue
                return_code, message = self.process_user_input(user_input)
                if return_code == 0:
                    continue
                if return_code == -1:
                    color.information(message)
                    continue
                if return_code == -2:
                    color.error(message)
                    continue
                if return_code == -3:
                    break
            except (EOFError, KeyboardInterrupt) as e:
                continue
