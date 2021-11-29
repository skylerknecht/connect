import threading

from connect import connection, server, stagers, util

class Engine():

    connections = {}
    STAGERS = {}

    def __init__(self, ip, port, cli):
        self.cli = cli
        self.ip = ip
        self.port = port
        self.STAGERS = {
            util.generate_id():stagers.JScriptStager(ip, port),
            util.generate_id():stagers.MSHTAStager(ip, port),
            util.generate_id():stagers.PYTHONStager(ip, port)
        }

    def create_connection(self, stager):
        _connection = connection.Connection(stager)
        self.connections[_connection.connection_id] = _connection
        self.cli.update_options(_connection.connection_id, _connection.interact, 'Interactive Connection', 'NOP-tions')
        return _connection

    def display_connections(self):
        if not self.connections:
            return -1, 'No connections to display.'
        self.cli.header('Connections')
        self.cli.print('default', '{:<13} {:<18} {:<13} {:<16} {:<13}'.format('ID', 'IP', 'Format', 'Status', 'Checkin'))
        for _, connection in self.connections.items():
            if connection.status == 'pending':
                self.cli.print('default', f'{connection}')
                continue
            if connection.disconnected():
                self.cli.print('disconnected', f'{connection}')
                continue
            if connection.stale():
                self.cli.print('stale', f'{connection}')
                continue
            if connection.status == 'connected':
                self.cli.print('connected', f'{connection}')
                continue
        self.cli.print('default', '')
        return 0, 'Success'

    def display_stagers(self):
        windows_deliveries = []
        linux_deliveries = []
        for stager_id, stager in self.STAGERS.items():
            for delivery in stager.deliveries:
                platform = delivery[0]
                _delivery = delivery[1].replace('-endpoint-', stager_id)
                if 'Windows' == platform:
                    windows_deliveries.append(_delivery)
                if 'Linux'== platform:
                    linux_deliveries.append(_delivery)
        self.cli.header('Windows Stagers')
        for delivery in windows_deliveries:
            self.cli.print('default', f' - {delivery}')
        self.cli.header('Linux Stagers')
        for delivery in linux_deliveries:
            self.cli.print('default', f' - {delivery}')
        self.cli.print('default', '')
        return 0, 'Success'

    def retrieve_stager(self, stager_format):
        formats = []
        for stager_id, stager in self.STAGERS.items():
            formats.append(stager.format)
            if stager_format == stager.format:
                return stager
        self.cli.print('information', f'Could not find a {stager_format} stager, valid stagers: {formats}')
        return None

    def run(self):
        ''' Setting up the server. '''
        server.engine = self
        _connect_server = threading.Thread(target=server.run, args=((self.ip, self.port)))
        _connect_server.daemon = True
        _connect_server.start()

        ''' Setting up the command line. '''
        self.cli.update_options('connections', self.display_connections, 'Displays current connections.', 'Engine Options')
        self.cli.update_options('server', server.interact, 'Interact with the server.', 'Engine Options')
        self.cli.update_options('stagers', self.display_stagers, 'Displays staged files ready for delivery.', 'Engine Options')
        self.cli.run()
        return
