from connect.constants import BANNER

__version__ = '0.0.1'
debug_level = 2


def set_debug_level(level: int):
    global debug_level
    debug_level = level


def get_debug_level():
    global debug_level
    return debug_level


# Clean up the Code
# Invalid Result Types cause Stack Trace
# Any other Stack Traces?
# Invalid Listener port ip?
# remove json.dumps for socketio