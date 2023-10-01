import readline
import threading

COLORS = {
    'bold': '\001\033[1m\002',
    'blue': '\001\033[94m\002',
    'green': '\001\033[92m\002',
    'purple': '\001\033[95m\002',
    'red': '\001\033[91m\002',
    'reset': '\001\033[0m\002',
    'underline': '\001\033[4m\002',
    'white': '',
    'yellow': '\001\033[93m\002'
}

NOTIFICATIONS = {
    'DEFAULT': '',
    'WARN': f"{COLORS['bold']}[!]{COLORS['reset']} ",
    'ERROR': f"{COLORS['red']}[-]{COLORS['reset']} ",
    'INFORMATION': f"{COLORS['blue']}[*]{COLORS['reset']} ",
    'SUCCESS': f"{COLORS['green']}[+]{COLORS['reset']} ",
    'STATUS': f"{COLORS['yellow']}[#]{COLORS['reset']} "
}

ORIGINAL_THREAD_IDENTIFIER = threading.current_thread().ident


def colorize(string: str, color: str, bold: bool = False) -> str:
    """
    Apply ANSI color and formatting to the input text.

    This function takes an input string and applies ANSI color and formatting based on the provided color and bold options.

    Parameters:
        string (str): The input string that needs to be colorized.
        color (str): The color to be applied to the input text. The available color options are 'white', 'red', 'green', 'yellow', 'blue', and 'purple'.
        bold (bool, optional): A boolean flag indicating whether to make the text bold (True) or not bold (False).

    Returns:
        str: The colorized input string with ANSI escape codes.

    Note:
        The color and formatting will be applied using ANSI escape codes. Make sure to print the returned string to a terminal or console that supports ANSI escape codes to see the colorized output correctly.
    """

    if color not in COLORS:
        color_keys = ', '.join(COLORS.keys())
        raise ValueError(f"Invalid color {color}. Available colors are: {color_keys}")
    formatted_string = f'{COLORS[color]}{string}{COLORS["reset"]}'
    if bold:
        formatted_string = f'{COLORS["bold"]}{formatted_string}'
    return formatted_string


def display(stdin: str, notification_type: str = 'DEFAULT', prefix: bool = True, end: str = '\n'):
    """
    Display a notification with an optional prefix. 

    Parameters:
        stdin (str): The main content of the notification message.
        notification_type (str): The type of the notification to display.
                                 Must be one of the keys in the NOTIFICATIONS dictionary.
                                 Defaults to INFORMATION
        prefix (bool, optional): If True, the notification will be prefixed according to the type.
                                 If False, the notification will be displayed without a prefix.
                                 Defaults to True.
        end (str, optional): The character to append at the end of the displayed message.
                             Defaults to '\\n'.
    """
    if notification_type not in NOTIFICATIONS:
        notification_keys = ', '.join(NOTIFICATIONS.keys())
        raise ValueError(
            f'Invalid notification type {notification_type}. Available notifications are: {notification_keys}')
    notification = stdin
    if prefix:
        notification = f'{NOTIFICATIONS[notification_type]}{stdin}'
    print(notification, end=end)
