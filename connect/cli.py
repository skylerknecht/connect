import connect
import connect.color as color
import connect.engine as engine
import re
import readline
import sys

banner = '''\n╔═╗┌─┐┌┐┌┌┐┌┌─┐┌─┐┌┬┐\n║  │ │││││││├┤ │   │\n╚═╝└─┘┘└┘┘└┘└─┘└─┘ ┴\n'''
command_history = []
menu_options = {}

HISTORY_REGEX = re.compile(r'history\s\d')

def complete_command(incomplete_option, state):
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
        finished_option = [option + ' ' for option in menu_options if option.startswith(incomplete_option)]
        return finished_option[state]
    if len(current_line_list) >= 2 and [option for option in menu_options if option.startswith(current_line)]:
        valid_options = [option for option in menu_options if len(option.split()) >= len(current_line_list)]
        finished_option = [option.split()[len(current_line_list) - 1] + ' ' for option in valid_options if option.split()[len(current_line_list) - 1].startswith(incomplete_option)]
        return finished_option[state]
    return 0

def display_command_history():
    color.display_banner('Command History')
    for number, command in enumerate(command_history):
        color.normal(f'{number} : {command}')
    color.normal('')
    return 0

def display_banner():
    color.normal(banner)
    return 0

def exit():
    return 1

def help_menu():
    color.display_banner('Help Menu')
    for option, option_description in menu_options.items():
        color.normal(f'\'{option}\': {option_description[1]}')
    color.normal('')
    return 0

def process_user_input(user_input):
    try:
        if HISTORY_REGEX.match(user_input):
            user_input = command_history[int(user_input.split(" ")[1])]
        return menu_options[user_input][0]()
    except KeyError:
        color.error('Invalid command.')
        return 0

def setup_menu():
    menu_options['?'] = (help_menu, 'Displays the help menu.')
    menu_options['connections'] = (engine.display_connections, 'Displays current connections.')
    menu_options['exit'] = (exit, 'Exits the current process.')
    menu_options['help'] = (help_menu, 'Displays the help menu.')
    menu_options['history'] = (display_command_history, 'Displays the command history. Execute a previous command by appending an index (e.g., history 0)')
    menu_options['implants'] = (engine.display_implants, 'Displays hosted implants ready for delivery.')
    menu_options['version'] = (version, 'Display the current application version.')

def setup_readline():
    readline.parse_and_bind('tab: complete')
    readline.set_completer(complete_command)
    readline.set_completer_delims(" \t\n\"\\'`@$><=;|&{(")

def version():
    color.normal(connect.__version__)
    return 0

def run():
    setup_menu()
    setup_readline()
    while True:
        try:
            user_input = color.display_prompt('connect~#').lower()
            if not user_input:
                continue
            if user_input not in command_history:
                command_history.append(user_input)
            return_code = process_user_input(user_input)
            if return_code > 0:
                break
        except (EOFError, KeyboardInterrupt) as e:
            color.information('Are you sure you want to quit? [Yes/No]')
            user_input = color.display_prompt('connect~#')
            if user_input == 'Yes':
                break
            continue
