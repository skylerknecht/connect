import argparse

from . import http_listener
from connect import BANNER

parser = argparse.ArgumentParser(description=BANNER, formatter_class=argparse.RawTextHelpFormatter,
                                 usage=argparse.SUPPRESS)
parser.add_argument('--ip', metavar='ip', help='Server ip.', default='127.0.0.1')
parser.add_argument('--port', metavar='port', help='Server port.', default=8080)
parser.add_argument('--ssl', nargs=2, metavar=('CERT', 'KEY'), help='Use SSL.')
parser.add_argument('--debug', action='store_true', help='Enable debug mode.')
http_listener.run(parser.parse_args())