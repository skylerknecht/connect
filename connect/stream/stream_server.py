import json
import asyncio
import socket
import ipaddress

from .stream_client import StreamClient
from connect.output import display
from connect.convert import base64_to_bytes


class StreamServer:

    def __init__(self, agent_id, connection_string, sio_server):
        self.connection_string = connection_string
        self.sio_server = sio_server
        self.stream_clients = {}
        self.listening = True
        self.agent_id = agent_id
        self.lhost = None
        self.lport = None
        self.rhost = None
        self.rport = None
        self.parse_connection_string(connection_string)

    @staticmethod
    def validate_ip(ip_str):
        try:
            # Use the ipaddress module to validate the IP address
            ipaddress.ip_address(ip_str)
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_port(port_str):
        try:
            port = int(port_str)
            return 0 <= port <= 65535
        except ValueError:
            return False

    def handle_stream_downstream(self, results):
        stream_client_id = results['client_id']
        if stream_client_id not in self.stream_clients:
            return
        self.stream_clients[stream_client_id].downstream_buffer.append(base64_to_bytes(results['data']))

    async def handle_stream_disconnect(self, results):
        stream_client_id = results['client_id']
        if stream_client_id not in self.stream_clients:
            return
        self.stream_clients[results['client_id']].client_socket.close()
        del self.stream_clients[results['client_id']]

    def parse_connection_string(self, connection_string):
        raise NotImplementedError("Server has not implemented parse_connection_string")


class RemoteStreamServer(StreamServer):
    STREAMER_TYPE = 'remote'

    def __init__(self, *args):
        super().__init__(*args)
        self.connect_results = []
        self.serve_requests = []

    async def start(self):
        self.serve_requests.append(json.dumps({
            'ip': self.rhost,
            'port': self.rport
        }))
        await self.sio_server.emit('information', f'Attempting to connect streamer {self.connection_string}')

    async def stop(self):
        await self.sio_server.emit('information', f'Attempting to shutdown streamer {self.connection_string}')
        self.listening = False
        for stream_client in self.stream_clients.values():
            stream_client.connected = False

    async def handle_stream_connect_request(self, request):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(1.0)
        try:
            await asyncio.to_thread(client_socket.connect, (self.lhost, self.lport))
            self.stream_clients[request['client_id']] = StreamClient(self.agent_id, client_socket)
            rep = 0
        except socket.error:
            rep = 1

        response_dict = {
            'atype': 1,
            'rep': rep,
            'bind_addr': None,
            'bind_port': None,
            'client_id': request['client_id']
        }

        self.connect_results.append(json.dumps(response_dict))

        if rep == 0:
            await self.stream_clients[request['client_id']].connect()


    def parse_connection_string(self, connection_string):
        # For remote streamers, expect both remote and local host/port (e.g., "192.168.1.20:9443:127.0.0.1:9050")
        parts = connection_string.split(':')
        if len(parts) != 4:
            raise ValueError("Invalid connection string for remote streamer.")

        self.rhost, self.rport, self.lhost, self.lport = parts
        self.lport = int(self.lport)
        self.rport = int(self.rport)

        # Validate rhost, rport, lhost, and lport
        if not self.validate_ip(self.rhost):
            raise ValueError(f"{self.rhost} is not a valid remote host")
        if not self.validate_port(self.rport):
            raise ValueError(f"{self.rport} is not a valid remote port")
        if not self.validate_ip(self.lhost):
            raise ValueError(f"{self.lhost} is not a valid local host")
        if not self.validate_port(self.lport):
            raise ValueError(f"{self.lport} is not a valid local port")


class LocalStreamServer(StreamServer):
    STREAMER_TYPE = 'local'

    def __init__(self, *args):
        super().__init__(*args)
        self.connect_requests = []
        self.socks_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socks_server.bind((self.lhost, self.lport))
        self.socks_server.settimeout(2.0)
        self.socks_server.listen(10)

    async def start(self):
        await self.sio_server.emit('success', f'Streamer {self.connection_string} is connected')
        while self.listening:
            try:
                client_socket, addr = await asyncio.to_thread(self.socks_server.accept)
            except socket.error:
                continue
            await asyncio.to_thread(self.handle_stream_client, client_socket)
        self.socks_server.close()

    async def stop(self):
        await self.sio_server.emit('success', f'Streamer {self.connection_string} is shutdown')
        self.listening = False
        for stream_client in self.stream_clients.values():
            stream_client.connected = False

    def handle_stream_client(self, client_socket):
        self.stream_clients[id(client_socket)] = StreamClient(self.agent_id, client_socket)
        self.connect_requests.append(json.dumps({
            'atype': 1,
            'address': self.rhost,
            'port': self.rport,
            'client_id': id(client_socket)
        }))

    async def handle_stream_connect_results(self, results):
        stream_client_id = results['client_id']
        if stream_client_id not in self.stream_clients:
            return
        await self.stream_clients[results['client_id']].connect()

    def parse_connection_string(self, connection_string):
        # For local streamers, expect both local and remote host/port (e.g., "127.0.0.1:9050:192.168.1.20:9443")
        parts = connection_string.split(':')
        if len(parts) != 4:
            raise ValueError("Invalid connection string for local streamer.")

        self.lhost, self.lport, self.rhost, self.rport = parts
        self.lport = int(self.lport)
        self.rport = int(self.rport)

        # Validate rhost, rport, lhost, and lport
        if not self.validate_ip(self.rhost):
            raise ValueError(f"{self.rhost} is not a valid remote host")
        if not self.validate_port(self.rport):
            raise ValueError(f"{self.rport} is not a valid remote port")
        if not self.validate_ip(self.lhost):
            raise ValueError(f"{self.lhost} is not a valid local host")
        if not self.validate_port(self.lport):
            raise ValueError(f"{self.lport} is not a valid local port")


class DynamicStreamServer(LocalStreamServer):
    STREAMER_TYPE = 'dynamic'
    SOCKS_VERSION = 5

    def __init__(self, *args):
        super().__init__(*args)
        self.atype_functions = {
            b'\x01': self._parse_ipv4_address,
            b'\x03': self._parse_domain_name,
            b'\x04': self._parse_ipv6_address
        }

    def parse_connection_string(self, connection_string):
        # For dynamic streamers, expect only a local host and port (e.g., "127.0.0.1:9050")
        parts = connection_string.split(':')
        if len(parts) != 2:
            raise ValueError(f"{connection_string} is not a valid connection string for {self.STREAMER_TYPE}.")

        self.lhost, self.lport = parts[0], int(parts[1])

        # Validate lhost and lport
        if not self.validate_ip(self.lhost):
            raise ValueError(f"{self.lhost} is not a valid local host")
        if not self.validate_port(self.lport):
            raise ValueError(f"{self.lport} is not a valid local port")

        # Set rhost and rport to '*' as required
        self.rhost, self.rport = '*', '*'

    def send_socks_connect_reply(self, results):
        identifier = results['client_id']
        atype = 1
        rep = results['rep']
        bind_addr = results['bind_addr'] if results['bind_addr'] else None
        bind_port = int(results['bind_port']) if results['bind_port'] else None
        reply = self.generate_reply(atype, rep, bind_addr, bind_port)
        self.stream_clients[identifier].client_socket.sendall(reply)

    async def handle_stream_connect_results(self, results):
        stream_client_id = results['client_id']
        if stream_client_id not in self.stream_clients:
            return
        self.send_socks_connect_reply(results)
        await self.stream_clients[results['client_id']].connect()

    async def handle_stream_disconnect_results(self, results):
        stream_client_id = results['client_id']
        if stream_client_id not in self.stream_clients:
            return
        self.send_socks_connect_reply(results)
        self.stream_clients[results['client_id']].client_socket.close()
        del self.stream_clients[results['client_id']]

    def handle_stream_client(self, client_socket):
        self.stream_clients[id(client_socket)] = StreamClient(self.agent_id, client_socket)
        self.parse_socks_connect(client_socket)

    def generate_reply(self, atype, rep, address, port):
        reply = b''.join([
            self.SOCKS_VERSION.to_bytes(1, 'big'),
            int(rep).to_bytes(1, 'big'),
            int(0).to_bytes(1, 'big'),
            int(atype).to_bytes(length=1, byteorder='big'),
            socket.inet_aton(address) if address else int(0).to_bytes(1, 'big'),
            port.to_bytes(2, 'big') if port else int(0).to_bytes(1, 'big')
        ])
        return reply

    def parse_address(self, client_socket):
        atype = client_socket.recv(1)
        try:
            address, port = self.atype_functions.get(atype)(client_socket), int.from_bytes(client_socket.recv(2), 'big',
                                                                                           signed=False)
            return atype, address, port
        except KeyError:
            client_socket.sendall(self.generate_reply(str(int.from_bytes(atype, byteorder='big')), 8, None, None))
            return None, None, None

    @staticmethod
    def _parse_ipv4_address(client_socket):
        return socket.inet_ntoa(client_socket.recv(4))

    @staticmethod
    def _parse_ipv6_address(client_socket):
        ipv6_address = client_socket.recv(16)
        return socket.inet_ntop(socket.AF_INET6, ipv6_address)

    @staticmethod
    def _parse_domain_name(client_socket):
        domain_length = client_socket.recv(1)[0]
        domain_name = client_socket.recv(domain_length).decode('utf-8')
        return domain_name

    @staticmethod
    def negotiate_cmd(client_socket):
        ver, cmd, rsv = client_socket.recv(3)
        return cmd == 1

    def negotiate_method(self, client_socket):
        try:
            ver, nmethods = client_socket.recv(2)
        except Exception:
            return False
        methods = [ord(client_socket.recv(1)) for _ in range(nmethods)]
        if 0 not in methods:
            client_socket.sendall(bytes([self.SOCKS_VERSION, int('FF', 16)]))
            return False

        client_socket.sendall(bytes([self.SOCKS_VERSION, 0]))
        return True

    def parse_socks_connect(self, client_socket):
        if not self.negotiate_method(client_socket):
            display(f"Socks client failed to negotiate method.", "ERROR")
            client_socket.close()
            return
        if not self.negotiate_cmd(client_socket):
            display(f"Socks client failed to negotiate cmd.", "ERROR")
            client_socket.close()
            return
        atype, address, port = self.parse_address(client_socket)
        if not address:
            display("Socks client failed to negotiate address.", "ERROR")
            client_socket.close()
            return
        self.connect_requests.append(json.dumps({
            'atype': int.from_bytes(atype, byteorder='big'),
            'address': address,
            'port': port,
            'client_id': id(client_socket)
        }))
