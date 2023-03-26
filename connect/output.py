import sys
import os

from collections import namedtuple

Agent = namedtuple('Agent', ['name', 'check_in', 'username', 'hostname', 'ip', 'os', 'options'])
AgentOption = namedtuple('AgentOption', ['name', 'description', 'parameters','type'])
Implant = namedtuple('Implant', ['id', 'key'])
Notification = namedtuple('Notification', ['prefix', 'color'])
Parameter = namedtuple('Parameter', ['name', 'description'])
Task = namedtuple('Task', ['name', 'description', 'paramters', 'type'])


"""
These ANSI Color Codes need to start with 001 and end with 002 so readline does not count the as characters.
Please see https://stackoverflow.com/a/55773513 for more information.
"""

COLORS = {
    'cyan':'\001\033[0;36m\002',
    'green':'\001\033[0;32m\002',
    'red':'\001\033[0;31m\002',
    'default':'\001\033[0;0m\002',
    'yellow':'\001\033[0;33m\002',
}

NOTIFICATIONS = {
    'DEFAULT': Notification('', COLORS['default']),
    'ERROR': Notification('[ERROR] ', COLORS['red']),
    'INFORMATION': Notification('[INFO] ', COLORS['yellow']),
    'SUCCESS': Notification('[SUCCESS] ', COLORS['green'])
}


def display(type: str, stdout: str, prefix_enabled: bool = True, newline: bool = True):
    if type == 'PROMPT':
        return input(stdout + ' ')
    try: 
        notification = NOTIFICATIONS[type]
    except KeyError:
        display('ERROR', f'Notification type: {type} does not exist.')
    prefix = notification.prefix if prefix_enabled else ''
    color = notification.color
    postfix = os.linesep if newline else '' 
    sys.stdout.write('\033[1K\r' + f'{color}{prefix}{stdout}\001\033[0m\002' + postfix)
    sys.stdout.flush()