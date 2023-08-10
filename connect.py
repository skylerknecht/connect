import argparse
import connect
import sys


def main():
    parser = argparse.ArgumentParser(description=connect.BANNER, formatter_class=argparse.RawTextHelpFormatter,
                                     usage=argparse.SUPPRESS)

    # setup connect argument switches for client and server.
    parser._positionals.title = 'Connect Tools'
    subparser = parser.add_subparsers(dest='tool', required=True)
    for tool in connect.SUPPORTED_TOOLS.values():
        tool.setup_parser(subparser)
    if len(sys.argv) == 1:  # if there are no arguments provided display the help menu.
        parser.print_help()
        return
    arguments = parser.parse_args()
    tool = connect.SUPPORTED_TOOLS.get(arguments.tool)
    tool.run(arguments)


if __name__ == '__main__':
    sys.exit(main())
