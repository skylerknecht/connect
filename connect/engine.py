import threading

from connect import color, connection, server, stagers, util

class Engine():

    connections = {}
    STAGERS = {}

    def __init__(self, ip, port, cli):
        self.cli = cli
        self.ip = ip
        self.port = port
        self.STAGERS = {
            util.generate_id():(stagers.JScriptStager(ip, port)),
            util.generate_id():(stagers.MSHTAStager(ip, port))
        }

    def create_connection(self, stager):
        _connection = connection.Connection(stager)
        self.connections[_connection.connection_id] = _connection
        self.cli.update_options({_connection.connection_id: util.MenuOption(_connection.interact, 'Interactive Connection', 'NOP-tions', color.normal, False)})
        return _connection

    def display_connections(self):
        if not self.connections:
            return -1, 'No connections to display.'
        color.header('Connections')
        color.normal('{:<13} {:<18} {:<13} {:<16} {:<13}'.format('ID', 'IP', 'Format', 'Status', 'Checkin'))
        for _, connection in self.connections.items():
            if connection.status == 'pending':
                color.normal(f'{connection}')
                continue
            if connection.disconnected():
                color.error(f'{connection}', symbol=False)
                continue
            if connection.stale():
                color.information(f'{connection}', symbol=False)
                continue
            if connection.status == 'connected':
                color.success(f'{connection}', symbol=False)
                continue
        color.normal('')
        return 0, 'Success'

    def display_stagers(self):
        color.header('Stagers')
        for stager_id, stager in self.STAGERS.items():
            endpoint = f'{util.server_context()}://{self.ip}:{self.port}/{stager_id}'
            color.normal(f'{stager.format}:')
            for delivery in stager.deliveries:
                _delivery = delivery.replace('-endpoint-', endpoint)
                color.normal(f' - {_delivery}')
            color.normal('')
        return 0, 'Success'

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
