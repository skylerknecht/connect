import argparse
import connect
import cmd2

from cmd2 import CommandSet, with_default_category, with_argparser
from requests import post


def post_job(job):
    """ Excepts a job of the following format: "name":"<name>", "arguments":"[argument, argument]" """
    post(f'{connect.client.server_uri}/jobs',
         f'{{"api_key":"{connect.client.api_key}", "connection_id": "{connect.client.current_connection}", {job} }}')


argparser = argparse.ArgumentParser()


@with_argparser(argparser)
@with_default_category('Standard API')
class STDAPICommands(CommandSet):
    def __init__(self):
        super().__init__()

    """ 
    Whoami Command 
    """

    def do_whoami(self, _: cmd2.Statement):
        """ Retrieve the username of the current user. """
        if not connect.client.current_connection:
            print('Please select a connection with \'*<connection_id>\'')
            return
        post_job('"name":"whoami","arguments":""')

    """ 
    Sleep Command 
    """

    argparser = argparse.ArgumentParser()
    argparser.add_argument('sleep', help='amount of time in milliseconds to sleep for')

    @with_argparser(argparser)
    def do_sleep(self, ns: argparse.Namespace):
        """ Change the check_in interval in milliseconds (e.g., 5000 is 5 seconds). """
        if not connect.client.current_connection:
            print('Please select a connection with \'*<connection_id>\'')
            return
        post_job(f'"name":"sleep","arguments":"{ns.sleep}"')
