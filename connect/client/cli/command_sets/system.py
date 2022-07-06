from cmd2 import CommandSet, Statement, with_default_category


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
        """ Retrieves current process information. """
        self.post_job(f'"name":"ps","arguments":"","type":1')

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

    """
    PWD Command
    """

    def do_pwd(self, _: Statement):
        """ Retrieve the current working directory. """
        self.post_job(f'"name":"pwd","arguments":"","type":1')