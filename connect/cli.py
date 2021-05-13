import re
import readline
import sys
import time

from connect import color, engine

HISTORY_REGEX = re.compile(r'history\s\d')

menu_options = {}
command_history = {}

def display_command_history():
    for number, command in command_history.items():
        color.normal(f'{number} : {command}')
    return 0

def exit():
    return 1

def help_menu():
    for option, option_description in menu_options.items():
        color.normal(f'\'{option}\': {option_description[1]}')
    return 0

def process_user_input(user_input, historical_command=False):
    try:
        if historical_command:
            user_input = command_history[int(user_input.split(" ")[1])]
        return menu_options[user_input][0]()
    except KeyError:
        color.error('Invalid command.')
        return 0

def setup_normal_menu():
    menu_options['?'] = (help_menu, 'Displays the help menu.')
    menu_options['help'] = (help_menu, 'Displays the help menu.')
    menu_options['exit'] = (exit, 'Exits the current process.')
    menu_options['history'] = (display_command_history, 'Displays the command history. Execute a previous command by appending an index (e.g., history 0)')

def setup_readline():
    readline.parse_and_bind("tab: complete")
    readline.set_completer(tab_complete)

def setup_server_menu(connect_server):
    menu_options['receive'] = (connect_server.receive_data, 'Attempts to receive data.')
    menu_options['check data'] = (connect_server.data_size, 'Retrieves the size of the data buffer.')

def tab_complete(incomplete_input, state):
    buffer = readline.get_line_buffer().split()
    current_options_index = len(buffer) - 1 # The current options are located at the length of the buffer - 1. (e.g. menu_options['option'].split()[0]) if we're looking for the first word in our command.
    if incomplete_input != buffer[-1]: # If the attempted tab completed string matches the last item in the buffer, set current_options to the length of the buffer (e.g. menu_options['option'].split()[1]) if we're looking for the second word in our command.
        current_options_index = len(buffer)
    valid_options = [option.split()[current_options_index] for option in menu_options.keys() if len(option.split()) >= len(buffer)]
    complete_input = [option for option in valid_options if option.startswith(incomplete_input)]
    return complete_input[state]

def run(connect_server):
    setup_readline()
    setup_normal_menu()
    setup_server_menu(connect_server)
    while True:
        user_input = color.display_terminal('connect~#').lower()
        if not user_input: # If there is no user input then continue to the next itteration of the while loop.
            continue
        historical_command = False
        if HISTORY_REGEX.match(user_input): # Does the command match r'history _number_' if so set historical_command to True.
            historical_command = True
        if user_input not in command_history.values(): # Append command to command_history if it does not already exist.
            command_history[len(command_history)] = user_input
        input_code = process_user_input(user_input, historical_command=historical_command)
        if input_code > 0: # If the input_code is positive break out of the while loop and exit graciously.
            break
