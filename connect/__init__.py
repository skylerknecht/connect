from connect.constants import BANNER

__version__ = '0.0.1'
debug_level = 2


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