import argparse

import asyncio
from . import pyplant
from connect import BANNER

parser = argparse.ArgumentParser(description=BANNER, formatter_class=argparse.RawTextHelpFormatter,
                                 usage=argparse.SUPPRESS)
parser.add_argument('url', metavar='url', help='Listener URL.')
parser.add_argument('key', metavar='key', help='Implant Key.')
parser.add_argument('--debug', action='store_true', help='Enable debug mode.')

asyncio.run(pyplant.run(parser.parse_args()))
