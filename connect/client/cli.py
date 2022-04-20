import argparse
import json
import datetime
import rich.box
import os
import connect.client
import connect.stagers.commands
import cmd2

from cmd2 import with_argparser, Fg, ansi
from requests import post
from rich.table import Table
from rich.console import Console
from typing import (
    Dict,
    List,
)

class Client(cmd2.Cmd):
    prompt = ansi.style('connect~# ', fg=Fg.DARK_GRAY)
    ruler = '·'
    console = Console()
    shortcuts = {'*': 'interact', '!': 'shell', '?': 'help -v'}
    CLIENT_CATEGORY = 'Main Menu'

    def __init__(self):
        super().__init__(allow_cli_args=False, shortcuts=self.shortcuts)
        self.api_key = connect.client.api_key
        self.server_uri = connect.client.server_uri
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
        for cmdset in self._installed_command_sets:
            if cmdset.cmd2_default_help_category == 'Standard API':
                self.disable_category(cmdset.cmd2_default_help_category, f'Not interacting with a connection.')
                continue
            self.disable_category(cmdset.cmd2_default_help_category,
                                  f'Not interacting with a {cmdset.cmd2_default_help_category} connection.')

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
            print('Result file does not exist.')
    argparser = argparse.ArgumentParser()

    @with_argparser(argparser)
    @cmd2.with_category(CLIENT_CATEGORY)
    def do_back(self, _):
        """Return to the main menu."""
        self.prompt = ansi.style(f'connect~# ', fg=Fg.DARK_GRAY)
        connection_type = connect.client.connections[connect.client.current_connection]
        self.disable_category('Standard API', f'Not interacting with a connection.')
        self.disable_category(connection_type, f'Not interacting with a {connection_type} connection.')
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
            self.enable_category('Standard API')
            self.enable_category(connection_type)
            self.prompt = ansi.style(f'({args.connection})~# ', fg=Fg.DARK_GRAY)
        except KeyError:
            print('Connection does not exist.')

    argparser = argparse.ArgumentParser()

    @with_argparser(argparser)
    @cmd2.with_category(CLIENT_CATEGORY)
    def do_connections(self, _):
        """ Display all connections. """
        response = post(f'{self.server_uri}/connections', f'{{"api_key":"{self.api_key}"}}')
        try:
            _connections = json.loads(response.text).items()
        except Exception:
            self.console.print('Not authenticated.')
            return
        table = Table(style="grey23")
        table.add_column('ID', justify='center')
        table.add_column('Type', justify='center')
        table.add_column('Check In', justify='center')
        table.add_column('Status', justify='center')
        table.add_column('Jobs', justify='center')
        table.box = rich.box.MINIMAL
        for identifier, connection in _connections:
            connect.client.connections.update({identifier: connection[2]})
            if connect.client.current_connection == identifier:
                identifier = f'* {identifier}'

            # If there is a check_in then should we display disconnected or connected?
            if connection[0]:
                check_in = datetime.datetime.fromisoformat(connection[0])
                time_delta = (datetime.datetime.now() - check_in)
                if time_delta.total_seconds() < 6:
                    table.add_row(identifier, connection[2], check_in.strftime('%m/%d/%Y %H:%M:%S %Z'), 'connected',
                                  str(connection[1]), style='green4')
                    continue
                if time_delta.total_seconds() > 6:
                    table.add_row(identifier, connection[2], check_in.strftime('%m/%d/%Y %H:%M:%S %Z'), 'disconnected',
                                  str(connection[1]), style='red3')
                    continue
            # If there is no check_in then display pending and not connected.
            table.add_row(identifier, connection[2], 'Not connected', 'pending', str(connection[1]),
                          style='deep_sky_blue3')
        self.console.print('')
        self.console.print(table)
        self.console.print('')

    argparser = argparse.ArgumentParser()

    @with_argparser(argparser)
    @cmd2.with_category(CLIENT_CATEGORY)
    def do_stagers(self, _):
        """ Display all stagers. """
        response = post(f'{self.server_uri}/routes', f'{{"api_key":"{self.api_key}"}}')
        try:
            _routes = json.loads(response.text).items()
        except Exception:
            self.console.print('Not authenticated.')
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
        self.console.print('')
        self.console.print(table)
        self.console.print('')

    argparser = argparse.ArgumentParser()

    @with_argparser(argparser)
    @cmd2.with_category(CLIENT_CATEGORY)
    def do_jobs(self, _):
        """ Display all jobs. """
        response = post(f'{self.server_uri}/jobs', f'{{"api_key":"{self.api_key}"}}')
        try:
            _jobs = json.loads(response.text).items()
        except Exception:
            self.console.print('Not authenticated.')
            return
        table = Table(style="grey23")
        table.add_column('Name', justify='center')
        table.add_column('Connection ID', justify='center')
        table.add_column('Status', justify='center')
        table.add_column('Time', justify='center')
        table.add_column('Results', justify='center')
        table.box = rich.box.MINIMAL
        print(_jobs)
        for identifier, job in _jobs:
            if connect.client.current_connection:
                if not str(job[1]) == connect.client.current_connection:
                    continue
            time = datetime.datetime.fromisoformat(job[3])
            if job[0] == 'check_in' or job[0] == 'downstream':
                continue
            if job[2] == 'completed':
                table.add_row(job[0], str(job[1]), job[2], time.strftime('%m/%d/%Y %H:%M:%S %Z'), job[4], style='green4')
                continue
            table.add_row(job[0], str(job[1]), job[2], time.strftime('%m/%d/%Y %H:%M:%S %Z'), job[4], style='deep_sky_blue3')
        self.console.print('')
        self.console.print(table)
        self.console.print('')
