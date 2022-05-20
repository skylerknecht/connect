import argparse

from connect.convert import string_to_base64
from connect.output import print_error
from cmd2 import Cmd2ArgumentParser, CommandSet, with_argparser, with_default_category


@with_default_category('Agent')
class AgentCommands(CommandSet):
    """
    The STDApi command set.
    """

    def __init__(self, post_job):
        super().__init__()
        self.post_job = post_job

    """ 
    Delay Command 
    """

    delay_parser = Cmd2ArgumentParser()
    delay_parser.add_argument('--sleep', metavar='sleep', help='amount of time in seconds to sleep for')
    delay_parser.add_argument('--jitter', metavar='jitter', help='percentage of sleep to add or subtract per check in')

    @with_argparser(delay_parser)
    def do_delay(self, args: argparse.Namespace):
        """ Change the sleep and jitter to alter the check_in interval. """
        if args.sleep:
            sleep = string_to_base64(str(float(args.sleep)))
            self.post_job(f'"name":"set sleep","arguments":"{sleep}","type":1')
        if args.jitter:
            if 0 > float(args.jitter) or float(args.jitter) > 100:
                print_error('Please set jitter to a number between 0 and 100 inclusive.')
                return
            jitter = string_to_base64(str(float(args.jitter)))
            self.post_job(f'"name":"set jitter","arguments":"{jitter}","type":1')
        if not args.jitter and not args.sleep:
            self.post_job(f'"name":"delay","arguments":"","type":1')

