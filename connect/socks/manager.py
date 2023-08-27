import os
import threading

from .socks import SocksServer
from collections import namedtuple
from connect.output import display
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


class SocksManager:
    socks_server = namedtuple('SocksServer', ['thread', 'socks_server'])
    socks_servers = {}

    def __init__(self):
        engine = create_engine(f'sqlite:///{os.getcwd()}/instance/connect.db')
        self.session = sessionmaker(bind=engine)()

    def create_socks_server(self, *args):
        new_socks_server = SocksServer(*args, self.session)
        socks_server_thread = threading.Thread(target=new_socks_server.listen_for_clients, daemon=True)
        socks_server_thread.start()
        self.socks_servers[args[2]] = self.socks_server(socks_server_thread, new_socks_server)

    def shutdown_socks_server(self, agent_id):
        self.socks_servers[agent_id].socks_server.shutdown()
        self.socks_servers[agent_id].thread.join()
        del self.socks_servers[agent_id]
        display(f'Successfully shutdown socks server for agent {agent_id}', 'SUCCESS')

    def shutdown_socks_servers(self):
        for socks_server in self.socks_servers:
            socks_server.socks_server.shutdown()
            socks_server.thread.join()

    def handle_socks_task_results(self, method, results):
        for socks_server in self.socks_servers.values():
            for socks_client in socks_server.socks_server.socks_clients:
                if socks_client.client_id == results['client_id']:
                    if method == 'socks_connect':
                        socks_client.handle_socks_connect_results(results)
                    if method == 'socks_downstream':
                        socks_client.handle_socks_downstream_results(results)