import argparse

from cmd2 import ansi, Cmd, Cmd2ArgumentParser, Fg, Statement, with_argparser
from connect import __version__ as version
from connect.output import print_error
from connect.convert import string_to_base64


class ConnectClient(Cmd):
    """
    The command line class for connect.
    """

    current_agent = ''
    agents = []
    team_server = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_category = 'Main Menu'
        self.delete_unused_commands()
        self.hide_commands(['set'])
        self.prompt = self._stylize_prompt("connect~# ")
        self.ruler = '·'

    @staticmethod
    def delete_unused_commands():
        """
        Remove unused commands inherited from cmd2.
        """
        del Cmd.do_edit
        del Cmd.do_alias
        del Cmd.do_py
        del Cmd.do_ipy
        del Cmd.do_macro
        del Cmd.do_run_pyscript
        del Cmd.do_run_script

    def disable_command_sets(self):
        """
        Disable all command sets.
        """
        for command_set in self._installed_command_sets:
            self.disable_category(command_set.cmd2_default_help_category, 'Not available.')

    def do_back(self, _: Statement):
        """
        Return to the main menu.
        """
        self.disable_command_sets()
        self.current_agent = ''
        self.prompt = self._stylize_prompt('connect~# ')

    def do_agents(self, _: Statement):
        """
        Print agents from the team server.
        """
        if not self.team_server:
            print_error('Not connected to the team listener.')
            return
        self.team_server.emit('agents')

    implants_argparser = Cmd2ArgumentParser()
    implants_argparser.add_argument('-c', '--create', metavar='COMMANDS',
                                    help='Create an implant by providing a command seperated list of commands.',
                                    nargs='+')

    # implants_argparser.add_argument('-d', '--delete', help='Delete an implant.')

    @with_argparser(implants_argparser)
    def do_implants(self, args: argparse.Namespace):
        """
        Print implants from the team server.
        """
        if not self.team_server:
            print_error('Not connected to the team listener.')
            return
        if args.create:
            commands = string_to_base64(','.join(args.create))
            commands = f'{{"create":"{commands}"}}'
            self.team_server.emit('implants', commands)
            return
        # todo Write delete implant functionality
        # if args.delete:
        #     print_error('Not implemented.')
        #     return
        self.team_server.emit('implants', data="")

    def complete_agents(self):
        """
        Complete the interact command.
        :return: Available agent names
        :rtype: list
        """
        return [_agent.name for _agent in self.agents]

    interact_argparser = Cmd2ArgumentParser()
    interact_argparser.add_argument('agent', choices_provider=complete_agents,
                                    help='The agent to interact with.')

    @with_argparser(interact_argparser)
    def do_interact(self, args: argparse.Namespace):
        """
        Interact with an agent.
        """
        self.disable_command_sets()
        _commands = None
        for _agent in self.agents:
            if _agent.name == args.agent:
                _commands = _agent.commands
        if not _commands:
            print_error('Agent does not exist.')
            return
        self.current_agent = args.agent
        self.prompt = self._stylize_prompt(f'({args.agent})~# ')
        self.enable_commands(_commands)

    def do_stagers(self, _: Statement):
        """
        Print stagers from the team listener.
        """
        if not self.team_server:
            print_error('Not connected to the team listener.')
            return
        self.team_server.emit('stagers')

    # noinspection PyMethodMayBeStatic
    def do_version(self, _: Statement):
        """
        Print the current version.
        """
        print(version)

    def enable_commands(self, _commands):
        """
        Enable commands.
        :param list _commands: A list commands to enable.
        """
        for command in self.get_all_commands():
            if command in _commands:
                self.enable_command(command)

    def enable_command_sets(self, _command_sets):
        """
        Enable all command set categories.
        :param list _command_sets: A list of command_sets to enable.
        """
        for command_set in _command_sets:
            self.enable_category(command_set)

    def hide_commands(self, _commands):
        """
        Hide commands from the operator.

        :param _commands: List of commands to hide.
        """
        for command in _commands:
            self.hidden_commands.append(command)

    @staticmethod
    def _stylize_prompt(_prompt: str, fg: Fg = Fg.DARK_GRAY) -> str:
        """
        Stylize a prompt with a foreground color.
        :param _prompt: The prompt to stylize.
        :param fg: The foreground color.
        :return: A cmd2 ansi style.
        :rtype: str
        """
        return ansi.style(_prompt, fg=fg)

    def do_quit(self, _: Statement):
        """
        Disconnects from the team server and quits the application.
        """
        self.team_server.disconnect()
        return True

    def do_exit(self, _: Statement):
        """
        Disconnects from the team server and quits the application.
        """
        self.team_server.disconnect()
        return True
