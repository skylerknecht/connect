#!/usr/bin/env -S python3 -B
import argparse
import sys
import json
import cmd2
import datetime

from requests import post
from rich.table import Table
from rich.console import Console
from cmd2 import (
    Bg,
    Fg,
    ansi,
)


class Client(cmd2.Cmd):
    connections = []
    current_connection = ''
    prompt = ansi.style('connect~# ', fg=Fg.LIGHT_CYAN)
    ruler = '-'
    console = Console()
    shortcuts = {'*': 'interact', '!': 'shell', '?': 'help -v'}
    CLIENT_CATEGORY = 'Client Commands'
    CONNECTION_CATEGORY = 'Connection Commands'

    def __init__(self, server_uri, api_key):
        super().__init__(allow_cli_args=False, shortcuts=self.shortcuts)
        self.api_key = api_key
        self.server_uri = server_uri
        del cmd2.Cmd.do_edit
        del cmd2.Cmd.do_alias
        del cmd2.Cmd.do_py
        del cmd2.Cmd.do_ipy
        del cmd2.Cmd.do_macro
        del cmd2.Cmd.do_run_pyscript
        del cmd2.Cmd.do_run_script
        del cmd2.Cmd.do_set
        cmd2.categorize((cmd2.Cmd.do_help, cmd2.Cmd.do_history, cmd2.Cmd.do_quit, cmd2.Cmd.do_shell,
                             cmd2.Cmd.do_shortcuts), self.CLIENT_CATEGORY)

    """ Connection Commands """

    @cmd2.with_category(CONNECTION_CATEGORY)
    def do_back(self, _):
        """ Return to the main menu. """
        self.prompt = ansi.style('connect~# ', fg=Fg.LIGHT_BLUE)
        self.current_connection = ''

    @cmd2.with_category(CONNECTION_CATEGORY)
    def do_whoami(self, _):
        """ Retrieve the username of the current user. """
        if not self.current_connection:
            print('Please select a connection with \'*<connection_id>\'')
            return
        post(f'{self.server_uri}/jobs',
             f'{{"api_key":"{self.api_key}", "connection_id": "{self.current_connection}", "name":"whoami", '
             f'"arguments":""}}')

    """ Client Commands """

    @cmd2.with_category(CLIENT_CATEGORY)
    def do_interact(self, connection):
        """ Interact with a connection. ( shortcut: * )"""
        if connection in self.connections:
            self.current_connection = connection
            self.prompt = ansi.style(f'({connection})~# ', fg=Fg.CYAN)

    @cmd2.with_category(CLIENT_CATEGORY)
    def do_connections(self, _):
        """ Display all connections. """
        response = post(f'{self.server_uri}/connections', f'{{"api_key":"{self.api_key}"}}')
        try:
            _connections = json.loads(response.text).items()
        except Exception:
            self.console.print('Not authenticated.')
            return
        table = Table(title='Connections')
        table.add_column('ID')
        table.add_column('Check In')
        table.add_column('Status')
        table.add_column('Jobs')
        for identifier, connection in _connections:
            self.connections.append(identifier)
            if self.current_connection == identifier:
                identifier = f'* {identifier}'
            if connection[0]:
                check_in = datetime.datetime.fromisoformat(connection[0])
                time_delta = (datetime.datetime.now() - check_in)
                if time_delta.total_seconds() < 6:
                    table.add_row(identifier, check_in.strftime('%m/%d/%Y %H:%M:%S %Z'), 'connected', str(connection[1]), style='green_yellow')
                    continue
                if time_delta.total_seconds() > 6:
                    table.add_row(identifier, check_in.strftime('%m/%d/%Y %H:%M:%S %Z'), 'disconnected', str(connection[1]), style='deep_pink2')
                    continue
            table.add_row(identifier, check_in.strftime('%m/%d/%Y %H:%M:%S %Z'), 'pending', str(connection[1]), style='deep_sky_blue3')
        self.console.print('')
        self.console.print(table)
        self.console.print('')

    @cmd2.with_category(CLIENT_CATEGORY)
    def do_stagers(self, _):
        """ Display all stagers. """
        response = post(f'{self.server_uri}/routes', f'{{"api_key":"{self.api_key}"}}')
        try:
            _routes = json.loads(response.text).items()
        except Exception:
            self.console.print('Not authenticated.')
            return
        table = Table(title='Stagers')
        table.add_column('Type')
        table.add_column('Staged URI')
        for identifier, route in _routes:
            if route[0] == 'check_in':
                continue
            table.add_row(route[0], f'{self.server_uri}/{identifier}', style='deep_sky_blue3')
        self.console.print('')
        self.console.print(table)
        self.console.print('')

    @cmd2.with_category(CLIENT_CATEGORY)
    def do_jobs(self, _):
        """ Display all jobs. """
        response = post(f'{self.server_uri}/jobs', f'{{"api_key":"{self.api_key}"}}')
        try:
            _jobs = json.loads(response.text).items()
        except Exception:
            self.console.print('Not authenticated.')
            return
        table = Table(title='Jobs')
        table.add_column('Name')
        table.add_column('Connection ID')
        table.add_column('Status')
        table.add_column('Results')
        for identifier, job in _jobs:
            if job[0] == 'check_in':
                continue
            if job[2] == 'completed':
                table.add_row(job[0], str(job[1]), job[2], job[3], style='green_yellow')
                continue
            table.add_row(job[0], str(job[1]), job[2], job[3], style='deep_sky_blue3')
        self.console.print('')
        self.console.print(table)
        self.console.print('')


def main():
    parser = argparse.ArgumentParser(add_help=False, description='Connect. Like your dots?')
    parser.add_argument('-h', '--help', action='help', help='Display this help message and exits.')
    parser.add_argument('server_uri', type=str, help='What server uri should we use?')
    parser.add_argument('api_key', type=int, help='What api_key should we use for authentication?')
    args = parser.parse_args()
    client = Client(args.server_uri, args.api_key)
    client.cmdloop()


if __name__ == '__main__':
    sys.exit(main())
