LEVEL_COLORS={
    'cyan':'\033[0;36m',
    'green':'\033[0;32m',
    'red':'\033[0;31m',
    'reset':'\033[0;0m',
}

def display_terminal():
    terminal_color = LEVEL_COLORS['cyan']
    reset = LEVEL_COLORS['reset']
    return input(f'{terminal_color}connect~#{reset} ')

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
