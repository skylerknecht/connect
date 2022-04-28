import argparse
import connect.routes.commands
import cmd2
import datetime
import json
import os
import rich.box
import socketio

from cmd2 import with_argparser, Fg, ansi
from requests import post
from rich.console import Console
from rich.table import Table

console = Console()
sio = socketio.Client()


@sio.event
def success(data):
    banner = data['banner']
    results = data['results']
    console.print(f'\n\n[+] {banner}\n', style='green3')
    print(f'{results}\n')


@sio.event
def failure(data):
    banner = data['banner']
    console.print(f'\n\n[-] {banner}\n', style='red4')

@sio.event
def information(data):
    banner = data['banner']
    console.print(f'\n\n[?] {banner}\n', style='deep_sky_blue3')


class Client(cmd2.Cmd):
    """
    Connect client class that inherits CMD2.
    """
    prompt = ansi.style('connect~# ', fg=Fg.DARK_GRAY)
    ruler = '·'
    shortcuts = {'*': 'interact', '!': 'shell', '?': 'help -v'}
    CLIENT_CATEGORY = '[Main Menu]'

    def __init__(self):
        super().__init__(allow_cli_args=False, shortcuts=self.shortcuts)
        self.api_key = connect.client.api_key
        self.server_uri = connect.client.server_uri
        try:
            sio.connect(connect.client.server_uri)
        except Exception as e:
            print(f'Failed to connect to the server. {e}')
        self.hidden_commands.append('set')
        del cmd2.Cmd.do_edit
        del cmd2.Cmd.do_alias
        del cmd2.Cmd.do_py
        del cmd2.Cmd.do_ipy
        del cmd2.Cmd.do_macro
        del cmd2.Cmd.do_run_pyscript
        del cmd2.Cmd.do_run_script
        cmd2.categorize((cmd2.Cmd.do_help, cmd2.Cmd.do_history, cmd2.Cmd.do_quit, cmd2.Cmd.do_shell,
                         cmd2.Cmd.do_shortcuts), self.CLIENT_CATEGORY)
        self.disable_categories()

    def disable_categories(self):
        for cmdset in self._installed_command_sets:
            if cmdset.cmd2_default_help_category == '[Standard API]':
                self.disable_category(cmdset.cmd2_default_help_category, f'Not interacting with a connection.')
                continue
            self.disable_category(cmdset.cmd2_default_help_category,
                                  f'Not interacting with a {cmdset.cmd2_default_help_category} connection.')

    quit_parser = argparse.ArgumentParser(description="Exit this application")

    @with_argparser(quit_parser)
    @cmd2.with_category(CLIENT_CATEGORY)
    def do_quit(self, _: argparse.Namespace):
        """Exit this application"""
        sio.disconnect()
        # Return True to stop the command loop
        self.last_result = True
        return True

    def complete_connections(self):
        return connect.client.connections

    def complete_result_files(self):
        return os.listdir(connect.client.downloads_directory)

    argparser = argparse.ArgumentParser()
    argparser.add_argument('file', choices_provider=complete_result_files, help='results to display')

    @with_argparser(argparser)
    @cmd2.with_category(CLIENT_CATEGORY)
    def do_results(self, args):
        """Display results from a file."""
        try:
            with open(f'{connect.client.downloads_directory}/{args.file}', 'r') as fd:
                print(fd.read())
        except FileNotFoundError:
            console.print('Result file does not exist.')

    argparser = argparse.ArgumentParser()

    @with_argparser(argparser)
    @cmd2.with_category(CLIENT_CATEGORY)
    def do_back(self, _):
        """Return to the main menu."""
        self.prompt = ansi.style(f'connect~# ', fg=Fg.DARK_GRAY)
        self.disable_categories()
        connect.client.current_connection = ''

    argparser = argparse.ArgumentParser()
    argparser.add_argument('connection', choices_provider=complete_connections, help='connection to interact with')

    @with_argparser(argparser)
    @cmd2.with_category(CLIENT_CATEGORY)
    def do_interact(self, args):
        """ Interact with a connection. ( shortcut: * )"""
        try:
            connection_type = connect.client.connections[args.connection]
            connect.client.current_connection = args.connection
            self.disable_categories()
            self.enable_category('[Standard API]')
            self.enable_category(f'{connection_type}')
            self.prompt = ansi.style(f'({args.connection})~# ', fg=Fg.DARK_GRAY)
        except KeyError:
            console.print('Connection does not exist.')

    argparser = argparse.ArgumentParser()

    @with_argparser(argparser)
    @cmd2.with_category(CLIENT_CATEGORY)
    def do_connections(self, _):
        """ Display all connections. """
        response = post(f'{self.server_uri}/connections', f'{{"api_key":"{self.api_key}"}}')
        try:
            _connections = json.loads(response.text).items()
        except Exception:
            console.print('Not authenticated.')
            return
        table = Table(style="grey23")
        table.add_column('ID', justify='center')
        table.add_column('Type', justify='center')
        table.add_column('Check In', justify='center')
        table.add_column('Status', justify='center')
        table.add_column('Username', justify='center')
        table.add_column('Hostname', justify='center')
        table.add_column('Operating System', justify='center')
        table.box = rich.box.MINIMAL
        for identifier, connection in _connections:
            connect.client.connections.update({identifier: connection[1]})
            if connect.client.current_connection == identifier:
                identifier = f'* {identifier}'

            # If there is a check_in then should we display disconnected or connected?
            if connection[0]:
                check_in = datetime.datetime.fromisoformat(connection[0])
                time_delta = (datetime.datetime.now() - check_in)
                if time_delta.total_seconds() <= 29:
                    table.add_row(identifier, connection[1], check_in.strftime('%m/%d/%Y %H:%M:%S %Z'), 'Connected',
                                  connection[2], connection[3], connection[4], style='green4')
                    continue
                if time_delta.total_seconds() > 29:
                    table.add_row(identifier, connection[1], check_in.strftime('%m/%d/%Y %H:%M:%S %Z'), 'Disconnected',
                                  connection[2], connection[3], connection[4], style='red3')
                    continue
            # If there is no check_in then display pending and not connected.
            table.add_row(identifier, connection[1], 'Not connected', 'Created', connection[2], connection[3],
                          connection[4],
                          style='deep_sky_blue3')
        console.print('')
        console.print(table)
        console.print('')

    argparser = argparse.ArgumentParser()

    @with_argparser(argparser)
    @cmd2.with_category(CLIENT_CATEGORY)
    def do_stagers(self, _):
        """ Display all stagers. """
        response = post(f'{self.server_uri}/routes', f'{{"api_key":"{self.api_key}"}}')
        try:
            _routes = json.loads(response.text).items()
        except Exception:
            console.print('Not authenticated.')
            return
        table = Table(style="grey23")
        table.add_column('Type', justify='center')
        table.add_column('Staged URI', justify='center')
        table.add_column('Description', justify='center')
        table.box = rich.box.MINIMAL
        for identifier, route in _routes:
            if route[0] == 'check_in':
                continue
            table.add_row(route[0], f'{self.server_uri}/{identifier}', route[1], style='deep_sky_blue3')
        console.print('')
        console.print(table)
        console.print('')
