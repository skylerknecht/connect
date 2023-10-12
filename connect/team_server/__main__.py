import argparse
import threading
import curses
import sys

from . import team_server
from connect import BANNER
from connect import decrease_debug_level, increase_debug_level

# Stop profiling and print the results
parser = argparse.ArgumentParser(description=BANNER, formatter_class=argparse.RawTextHelpFormatter,
                                 usage=argparse.SUPPRESS)
parser.add_argument('--ip', metavar='ip', help='Server ip.', default='127.0.0.1')
parser.add_argument('--port', metavar='port', help='Server port.', default=1337)
parser.add_argument('--ssl', nargs=2, metavar=('CERT', 'KEY'), help='Use SSL.')
threading.Thread(target=team_server.run, args=(parser.parse_args(),), daemon=True).start()
while True:
    try:
        user_input = input('(debug)~# ')
        if user_input == 'i':
            increase_debug_level()
        if user_input == 'd':
            decrease_debug_level()
    except KeyboardInterrupt:
        sys.exit()