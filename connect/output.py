from collections import namedtuple
from datetime import datetime
from rich import print, box, console
from rich.table import Table

ERROR = 'red3'
STATUS = 'deep_sky_blue3'
STALE = 'yellow2'
SUCCESS = 'green4'
TABLE_STYLE = 'grey23'

TIMESTAMP_FORMAT = '%m/%d/%Y %H:%M:%S %Z'

Agent = namedtuple('Agent', ['name', 'check_in', 'username', 'hostname', 'pid', 'integrity',
                             'commands', 'sleep', 'jitter'])
Stager = namedtuple('Stager', ['type', 'endpoints'])
Implant = namedtuple('Implant', ['key'])


def agents_table():
    """
    Generate a new connections table.

    :return: A newly defined connections table
    """
    _connections_table = Table(style=TABLE_STYLE)
    _connections_table.box = box.MINIMAL
    _connections_table.add_column('Name', justify='center')
    _connections_table.add_column('Delay', justify='center')
    _connections_table.add_column('Username', justify='center')
    _connections_table.add_column('Hostname', justify='center')
    _connections_table.add_column('PID', justify='center')
    _connections_table.add_column('Integrity', justify='center')
    return _connections_table


def stagers_table():
    """
    Generate a new stagers table.

    :return: A newly defined stagers table
    """
    _stagers_table = Table(style=TABLE_STYLE)
    _stagers_table.box = box.MINIMAL
    _stagers_table.add_column('Type', justify='center')
    _stagers_table.add_column('Endpoints', justify='center')
    return _stagers_table


def _from_is_iso_format(datetime_str: str) -> datetime:
    """
    Convert a datetime string to a datetime object from ISO format.

    :param str datetime_str: The datetime string to convert.
    :return: A datetime object.
    :rtype: datetime
    """
    return datetime.fromisoformat(datetime_str)


def _new_line():
    print('\n')


def print_agents_table(_agents: list, current_agent: str, current_connection_prefix='*'):
    """
    Print connections to the console.

    :param list _agents: The connections to print.
    :param str current_agent: The current connection.
    :param current_connection_prefix: The prefix to use for the current connection's row.
    """
    _new_line()
    _agents_table = agents_table()
    _style = STATUS
    for _agent in _agents:
        _prefix = ''
        _check_in = _from_is_iso_format(_agent.check_in)
        _check_in_delta = (datetime.now() - _check_in).total_seconds()
        _check_in_str = f'{int(_check_in_delta)} second(s)'
        _agent_max_delay = (float(_agent.sleep) * (float(_agent.jitter) / 100)) + float(_agent.sleep)
        if _check_in.timestamp() == 823879740.0:
            _check_in_str = '....'
            _style = STATUS
        elif _check_in_delta <= _agent_max_delay + 60.0:
            _style = SUCCESS
        elif _agent_max_delay + 60.0 < _check_in_delta < _agent_max_delay + 300.0:
            _style = STALE
        else:
            _style = ERROR
        if current_agent == _agent.name:
            _prefix = current_connection_prefix
        _agents_table.add_row(f'{_prefix} {_agent.name}', _check_in_str,
                              _agent.username, _agent.hostname, _agent.pid,
                              _agent.integrity, style=_style)
    print(_agents_table)


def print_stagers_table(stagers: list, server_uri):
    """
    Print stagers to the console.

    :param server_uri: The server's uri to use for the deliveries.
    :param list stagers: The stagers to print.
    """
    _new_line()
    _stagers_table = stagers_table()
    for _stager in stagers:
        _endpoints = _stager.endpoints.replace('~server_uri~', server_uri)
        _stagers_table.add_row(_stager.type, _endpoints, style=STATUS)
    print(_stagers_table)


def print_traceback():
    """
    Print traceback to the console.
    """
    _new_line()
    _console = console.Console()
    _console.print_exception(show_locals=True)
    _new_line()


def print_error(message: str):
    """
    Print an error message to the console.

    :param str message: The message to print.
    """
    prefix = '[-] '
    print(f'[bold {ERROR}]{prefix}{message}[/bold {ERROR}]')


def print_status(message: str):
    """
    Print a status message to the console.

    :param str message: The message to print.
    """
    prefix = '[*] '
    print(f'[bold {STATUS}]{prefix}{message}[/bold {STATUS}]')


def print_success(message: str):
    """
    Print a success message to the console.

    :param str message: The message to print.
    """
    prefix = '[+] '
    print(f'[bold {SUCCESS}]{prefix}{message}[/bold {SUCCESS}]')
