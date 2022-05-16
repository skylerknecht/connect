import argparse

from connect.convert import string_to_base64
from cmd2 import Cmd2ArgumentParser, CommandSet, Statement, with_argparser, with_default_category, Cmd


@with_default_category('Enumeration')
class EnumerationCommands(CommandSet):
    """
    The STDApi command set.
    """

    def __init__(self, post_job):
        super().__init__()
        self.post_job = post_job

    """ 
    PS Command 
    """

    def do_ps(self, _: Statement):
        """ Retrieves current process information. """
        self.post_job(f'"name":"ps","arguments":"","type":1')

    """ 
    Dir Command 
    """

    dir_parser = Cmd2ArgumentParser()
    dir_parser.add_argument('dir', help='the directory to inspect')

    @with_argparser(dir_parser)
    def do_dir(self, args: argparse.Namespace):
        """ List the contents and properties of a directory. """
        directory = string_to_base64(args.dir)
        self.post_job(f'"name":"dir","arguments":"{directory}","type":1')

    """
    Whoami Command
    """

    def do_whoami(self, _: Statement):
        """ Retrieve the username of the user. """
        self.post_job('"name":"whoami","arguments":"","type":1')

    """ 
    Hostname Command 
    """

    def do_hostname(self, _: Statement):
        """ Retrieve the hostname of the machine. """
        self.post_job('"name":"hostname","arguments":"","type":1')

    """
    OS Command
    """

    def do_os(self, _: Statement):
        """ Retrieve the operating system's product and build information. """
        self.post_job(f'"name":"os","arguments":"","type":1')
