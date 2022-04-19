import argparse
import connect.client as client
import sys


def main():
    parser = argparse.ArgumentParser(add_help=False, description='Connect. Like your dots?')
    parser.add_argument('-h', '--help', action='help', help='Display this help message and exits.')
    parser.add_argument('server_uri', type=str, help='What server uri should we use?')
    parser.add_argument('api_key', type=int, help='What api_key should we use for authentication?')
    args = parser.parse_args()
    client.server_uri = args.server_uri
    client.api_key = args.api_key
    client.run()


if __name__ == '__main__':
    sys.exit(main())