from connect.output import display
from connect.constants import BANNER

__version__ = '0.0.1'
debug_level = 0

def increase_debug_level():
    global debug_level
    if debug_level == 5:
        display('Maximum debug level is five', 'WARN')
        return
    debug_level = debug_level + 1
    display(f'Debug level increased to {debug_level}', 'INFORMATION')

def decrease_debug_level():
    global debug_level
    if debug_level == 0:
        display('Minimum debug level is zero', 'WARN')
        return
    debug_level = debug_level - 1
    display(f'Debug level decreased to {debug_level}', 'INFORMATION')

def set_debug_level(level: int):
    global debug_level
    debug_level = level


def get_debug_level():
    global debug_level
    return debug_level


# ToDo Clean up the Code
# ToDo Invalid Result Types cause Stack Trace
# ToDo Any other Stack Traces?
# ToDo Invalid Listener port ip?
# ToDo remove json.dumps for socketio
# ToDo Reconnecting to team_server every CTRL+C
# ToDo Guardrails?
# ToDo Implant Profiles
# ToDo Update status messages