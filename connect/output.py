from rich import print, console

ERROR = 'red3'
STATUS = 'deep_sky_blue3'
STALE = 'yellow2'
SUCCESS = 'green4'
TABLE_STYLE = 'grey23'

TIMESTAMP_FORMAT = '%m/%d/%Y %H:%M:%S %Z'


def print_traceback():
    """
    Print traceback to the console.
    """
    traceback_console = console.Console()
    traceback_console.print_exception(show_locals=True)


def print_error(message: str):
    """
    Print an error message to the console.

    :param str message: The message to print.
    """
    prefix = '[ERROR] '
    print(f'[bold {ERROR}]{prefix}{message}[/bold {ERROR}]')


def print_debug(message: str, debug_mode: bool, prefix: bool=True, color: bool=True):
    """
    Print an error message to the console.

    :param str message: The message to print.
    :param bool debug_mode: Switch debug mode on / off.
    """
    if not debug_mode:
        return
    
    if prefix:
        prefix = '[DEBUG] '
    else:
        prefix = ''
        
    if color:
        print(f'[bold {STALE}]{prefix}{message}[/bold {STALE}]')
    else:
        print(f'{prefix}{message}')


def print_info(message: str):
    """
    Print a status message to the console.

    :param str message: The message to print.
    """
    prefix = '[INFO] '
    print(f'[bold {STATUS}]{prefix}{message}[/bold {STATUS}]')


def print_success(message: str):
    """
    Print a success message to the console.

    :param str message: The message to print.
    """
    prefix = '[SUCCESS] '
    print(f'[bold {SUCCESS}]{prefix}{message}[/bold {SUCCESS}]')
