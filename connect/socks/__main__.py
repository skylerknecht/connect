import argparse

from . import cli
from connect import BANNER

parser = argparse.ArgumentParser(description=BANNER, formatter_class=argparse.RawTextHelpFormatter,
                                 usage=argparse.SUPPRESS)
parser.add_argument('key', metavar='key', help='Team Server Key.', default='8080')
parser.add_argument('--url', metavar='url', help='Team Server URL.', default='http://127.0.0.1:1337/')
parser.add_argument('--no-server', action='store_true', help='Don\'t connect to the team server.')

cli.run(parser.parse_args())