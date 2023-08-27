from connect.constants import BANNER

__version__ = '0.0.1'
debug_level = 2


def set_debug_level(level: int):
    global debug_level
    debug_level = level


def get_debug_level():
    global debug_level
    return debug_level
