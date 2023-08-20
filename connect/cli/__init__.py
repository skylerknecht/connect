from connect.cli.cli import CLI
from .commands import COMMANDS


cli = CLI('cli', '(connect)~# ', COMMANDS)
