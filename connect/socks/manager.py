from collections import namedtuple
from .socks import SocksServer


class SocksManager:
    socks_server = namedtuple('SocksServer', ['socks_server_thread', 'socks_server'])

    def __init__(self):
        self.socks_servers = {}

    async def create_socks_server(self, agent_id, address, port, sio_team_server):
        if agent_id in self.socks_servers:
            socks_server = self.socks_servers[agent_id].socks_server
            if socks_server.server_is_listening():
                await sio_team_server.emit('error', f'{agent_id} is already connected to socks5://{socks_server.address}:{socks_server.port}')
                return
        try:
            new_socks_server = SocksServer(address, port)
            await sio_team_server.emit('success', f'{agent_id} is connected to socks5://{address}:{port}')
        except Exception as e:
            await sio_team_server.emit('error', f'{agent_id} failed to start a socks server: {e}')
            return

        self.socks_servers[agent_id] = new_socks_server
        await new_socks_server.listen_for_clients()

    async def shutdown_socks_server(self, agent_id, sio_team_server):
        try:
            socks_server = self.socks_servers[agent_id]
        except KeyError:
            await sio_team_server.emit('error', f'{agent_id} failed to shutdown socks server. No server exists.')
            return

        if socks_server.server_is_listening():
            socks_server.shutdown()
            await sio_team_server.emit('success', f'{agent_id} successfully shutdown socks server socks5://{socks_server.address}:{socks_server.port}')

        del self.socks_servers[agent_id]

    def shutdown_socks_servers(self):
        for agent_id, socks_server in self.socks_servers.items():
            if socks_server.server_is_listening():
                socks_server.shutdown()
                del self.socks_servers[agent_id]

    def handle_socks_task_results(self, method, results):
        for socks_server in self.socks_servers.values():
            for socks_client in socks_server.socks_clients:
                if socks_client.client_id == results['client_id']:
                    if method == 'socks_connect':
                        socks_client.handle_socks_connect_results(results)
                    if method == 'socks_downstream':
                        socks_client.handle_socks_downstream_results(results)

    def server_is_listening(self, agent_id):
        if agent_id in self.socks_servers:
            return self.socks_servers[agent_id].server_is_listening()
        return False

    def get_socks_tasks(self, agent_id):
        socks_tasks = []
        if agent_id in self.socks_servers:
            for socks_client in self.socks_servers[agent_id].socks_clients:
                while socks_client.socks_tasks:
                    socks_tasks.append(socks_client.socks_tasks.pop(0))
        return socks_tasks
