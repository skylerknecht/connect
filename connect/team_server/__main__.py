import argparse

from . import team_server
from connect import BANNER

parser = argparse.ArgumentParser(description=BANNER, formatter_class=argparse.RawTextHelpFormatter,
                                 usage=argparse.SUPPRESS)
parser.add_argument('--ip', metavar='ip', help='Server ip.', default='127.0.0.1')
parser.add_argument('--port', metavar='port', help='Server port.', default=1337)
parser.add_argument('--ssl', nargs=2, metavar=('CERT', 'KEY'), help='Use SSL.')
parser.add_argument('--debug', action='store_true', help='Enable debug mode.')
team_server.run(parser.parse_args())