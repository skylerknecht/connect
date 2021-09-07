import sys

from connect import util

COLORS={
    'cyan':'\001\033[0;36m\002',
    'green':'\001\033[0;32m\002',
    'red':'\001\033[0;31m\002',
    'reset':'\001\033[0;0m\002',
    'yellow':'\001\033[0;33m\002',
    'purple':'\001\033[0;35m\002'
}

def error(message, symbol=True):
    message_color = COLORS['red']
    reset = COLORS['reset']
    output_str = f'{message_color}{message}{reset}'
    if symbol:
        output_str = f'{message_color}[-] {message}{reset}'
    print(output_str)
    return


def header(header):
    message_color = COLORS['reset']
    reset = COLORS['reset']
    dash = '='
    print('')
    print(f'{message_color}{header}{reset}')
    print(f'{dash*len(header)}')
    print('')

def information(message, symbol=True, user_input=False, end='\n'):
    message_color = COLORS['yellow']
    reset = COLORS['reset']
    output_str = f'{message_color}{message}{reset}'
    if symbol:
        output_str = f'{message_color}[!] {message}{reset}'
    if user_input:
        return input(f'\n{output_str}')
    print(output_str, end=end)
    return

def normal(message):
    message_color = COLORS['reset']
    reset = COLORS['reset']
    print(f'{message_color}{message}{reset}')

def prompt(message):
    terminal_color = COLORS['cyan']
    reset = COLORS['reset']
    return input(f'{terminal_color}{message}{reset} ')

def success(message, symbol=True):
    message_color = COLORS['green']
    reset = COLORS['reset']
    output_str = f'{message_color}{message}{reset}'
    if symbol:
        output_str = f'{message_color}[+] {message}{reset}'
    print(output_str)
    return

def unloaded(message):
    message_color = COLORS['purple']
    reset = COLORS['reset']
    output_str = f'{message_color}{message}{reset}'
    print(output_str)

def verbose(message):
    if not util.verbose:
        return
    message_color = COLORS['yellow']
    reset = COLORS['reset']
    output_str = f'{message_color}[!] {message}{reset}'
    print(output_str)
