LEVEL_COLORS={
    'cyan':'\001\033[0;36m\002',
    'green':'\001\033[0;32m\002',
    'red':'\001\033[0;31m\002',
    'reset':'\001\033[0;0m\002',
}

def display_prompt(message):
    terminal_color = LEVEL_COLORS['cyan']
    reset = LEVEL_COLORS['reset']
    return input(f'{terminal_color}{message}{reset} ')

def error(message):
    message_color = LEVEL_COLORS['red']
    reset = LEVEL_COLORS['reset']
    print(f'{message_color}[-] {message}{reset}')

def success(message):
    message_color = LEVEL_COLORS['green']
    reset = LEVEL_COLORS['reset']
    print(f'{message_color}[+] {message}{reset}')

def normal(message):
    message_color = LEVEL_COLORS['reset']
    reset = LEVEL_COLORS['reset']
    print(f'{message_color}{message}{reset}')
