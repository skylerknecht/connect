LEVEL_COLORS={
    'cyan':'\001\033[0;36m\002',
    'green':'\001\033[0;32m\002',
    'red':'\001\033[0;31m\002',
    'reset':'\001\033[0;0m\002',
    'yellow':'\001\033[0;33m\002',
    'blue':'\001\033[0;35m\002'
}

def display_banner(message):
    message_color = LEVEL_COLORS['reset']
    reset = LEVEL_COLORS['reset']
    dash = '='
    print(f'\n{message_color}{message}\n{dash*len(message)}\n{reset}')

def display_prompt(message, connection=None):
    terminal_color = LEVEL_COLORS['cyan']
    reset = LEVEL_COLORS['reset']
    if connection:
        return input(f'{terminal_color}connection{reset} ({connection.connection_id}) {reset}{terminal_color}: {reset}')
    return input(f'{terminal_color}{message}{reset} ')

def error(message):
    message_color = LEVEL_COLORS['red']
    reset = LEVEL_COLORS['reset']
    print(f'{message_color}[-] {message}{reset}')

def normal(message):
    message_color = LEVEL_COLORS['reset']
    reset = LEVEL_COLORS['reset']
    print(f'{message_color}{message}{reset}')

def success(message, symbol=True):
    message_color = LEVEL_COLORS['green']
    reset = LEVEL_COLORS['reset']
    if symbol:
        print(f'{message_color}[+] {message}{reset}')
        return
    print(f'{message_color}{message}{reset}')

def information(message, user_input=False):
    message_color = LEVEL_COLORS['yellow']
    reset = LEVEL_COLORS['reset']
    if user_input:
        return input(f'\n{message_color}[!] {message}{reset}')
    print(f'{message_color}[!] {message}{reset}')
