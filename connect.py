import argparse
import connect
import sys


def main():
    parser = argparse.ArgumentParser(description='connect', formatter_class=argparse.RawTextHelpFormatter,
                                     usage=argparse.SUPPRESS)

    # setup connect argument switches for client and server.
    parser._positionals.title = 'Connect Controllers'
    subparser = parser.add_subparsers(dest='controller', required=True)
    for controller in connect.SUPPORTED_CONTROLLERS.values():
        controller.setup_parser(subparser)
    if len(sys.argv) == 1:  # if there are no arguments provided display the help menu.
        parser.print_help()
        return
    arguments = parser.parse_args()
    controller = connect.SUPPORTED_CONTROLLERS.get(arguments.controller)
    controller.run(arguments)


if __name__ == '__main__':
    sys.exit(main())
