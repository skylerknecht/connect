from .stream_server import DynamicStreamServer


class StreamServerManager:

    def __init__(self, sio_server):
        self.sio_server = sio_server
        self.stream_servers = {}
        self.stream_server_types = {
            'dynamic': DynamicStreamServer
        }

    def get_streamers(self):
        """
        Get information about all managed streamers.

        Returns:
            list: A list of dictionaries containing information about each streamer.
        """
        streamer_info = []
        for streamer in self.stream_servers.values():
            info = {
                'agent': streamer.agent_id,
                'ip': streamer.address,
                'port': streamer.port,
            }
            streamer_info.append(info)
        return streamer_info

    def retrieve_stream_tasks(self, stream_server_id):
        stream_tasks = []
        if stream_server_id not in self.stream_servers:
            return stream_tasks
        stream_server = self.stream_servers[stream_server_id]
        for stream_client in stream_server.stream_clients.values():
            while stream_client.upstream_buffer:
                stream_tasks.append({
                    'event': 'stream_upstream',
                    'data': stream_client.upstream_buffer.pop(0)
                })
            if not stream_client.connected:
                stream_tasks.append({
                    'event': 'stream_disconnect',
                    'data': id(stream_client)
                })
        while stream_server.connect_requests:
            stream_tasks.append({
                'event': 'stream_connect',
                'data': stream_server.connect_requests.pop(0)
            })
        return stream_tasks

    async def create_stream_server(self, server_type: str, agent_id: str, ip: str, port: int):
        if server_type not in self.stream_server_types:
            await self.sio_server.emit('error', f'{server_type} is not a valid server type')
            return
        if agent_id in self.stream_servers:
            await self.sio_server.emit('error', f'{agent_id} is already streaming')
            return
        server = self.stream_server_types[server_type]
        try:
            server = server(agent_id, ip, port)
        except Exception as e:
            await self.sio_server.emit('error', f'Failed to start {server_type} on {ip}:{port} for {agent_id}: {e}')
            return
        self.stream_servers[agent_id] = server
        await self.sio_server.emit('success', f'Started {server_type} stream server on {ip}:{port} for {agent_id}')
        await server.start()

    async def handle_stream_connect(self, agent_id, results):
        if agent_id not in self.stream_servers:
            return
        await self.stream_servers[agent_id].handle_stream_connect(results)

    async def handle_stream_disconnect(self, agent_id, results):
        if agent_id not in self.stream_servers:
            return
        await self.stream_servers[agent_id].handle_stream_disconnect(results)

    def handle_stream_downstream(self, agent_id, results):
        if agent_id not in self.stream_servers:
            return
        self.stream_servers[agent_id].handle_stream_downstream(results)