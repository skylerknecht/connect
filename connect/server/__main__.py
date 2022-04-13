#!/usr/bin/env -S python3 -B
import argparse
import connect
import sys


def main():
    parser = argparse.ArgumentParser(add_help=False, description='Connect. Like your dots?')
    parser.add_argument('-h', '--help', action='help', help='Display this help message and exits.')
    parser.add_argument('ip', type=str, help='What ip should the server.py bind to?')
    parser.add_argument('port', type=int, help='What port should the server.py bind to?')
    parser.add_argument('--ssl', nargs=2, metavar=('CERT', 'KEY'),
                        help='What certificates should the server.py use for '
                             'encryption?')
    args = parser.parse_args()
    connect.server.run(args)


if __name__ == '__main__':
    sys.exit(main())
