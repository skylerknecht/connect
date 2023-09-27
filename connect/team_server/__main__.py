import argparse
import threading
import sys
import time

from . import team_server
from connect import BANNER
from connect.listener import listener_manager

parser = argparse.ArgumentParser(description=BANNER, formatter_class=argparse.RawTextHelpFormatter,
                                 usage=argparse.SUPPRESS)
parser.add_argument('--ip', metavar='ip', help='Server ip.', default='127.0.0.1')
parser.add_argument('--port', metavar='port', help='Server port.', default=1337)
parser.add_argument('--ssl', nargs=2, metavar=('CERT', 'KEY'), help='Use SSL.')
parser.add_argument('--debug', action='store_true', help='Enable debug mode.')
threading.Thread(target=team_server.run, args=(parser.parse_args(),), daemon=True).start()
while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        sys.exit()