import json
import asyncio
import socket

from .stream_client import StreamClient
from connect.output import display
from connect.convert import base64_to_bytes


class StreamServer:

    def __init__(self, agent_id, ip, port):
        self.connect_requests = []
        self.stream_clients = {}
        self.agent_id = agent_id
        self.address = ip
        self.port = int(port)

    def handle_stream_downstream(self, results):
        identifier = results['client_id']
        if identifier not in self.stream_clients:
            return
        self.stream_clients[identifier].downstream_buffer.append(base64_to_bytes(results['data']))

    async def handle_stream_connect(self, results):
        raise NotImplementedError("Server has not implemented handle_stream_connect")

    async def handle_stream_disconnect(self, results):
        raise NotImplementedError("Server has not implemented handle_stream_disconnect")


class LocalStreamServer(StreamServer):

    def __init__(self, agent_id, ip, port):
        super().__init__(agent_id, ip, port)
        self.listening = True
        self.socks_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socks_server.bind((self.address, self.port))
        self.socks_server.settimeout(2.0)
        self.socks_server.listen(10)

    async def start(self):
        while self.listening:
            try:
                client_socket, addr = await asyncio.to_thread(self.socks_server.accept)
            except socket.error:
                continue
            await asyncio.to_thread(self.handle_stream_client, client_socket)
        self.socks_server.close()

    def handle_stream_client(self, client_socket):
        raise NotImplementedError("Server has not implemented handle_stream_client")


class DynamicStreamServer(LocalStreamServer):
    SOCKS_VERSION = 5

    def __init__(self, agent_id, ip, port):
        super().__init__(agent_id, ip, port)
        self.atype_functions = {
            b'\x01': self._parse_ipv4_address,
            b'\x03': self._parse_domain_name,
            b'\x04': self._parse_ipv6_address
        }

    def send_socks_connect_reply(self, results):
        identifier = results['client_id']
        atype = 1
        rep = results['rep']
        bind_addr = results['bind_addr'] if results['bind_addr'] else None
        bind_port = int(results['bind_port']) if results['bind_port'] else None
        reply = self.generate_reply(atype, rep, bind_addr, bind_port)
        self.stream_clients[identifier].client_socket.sendall(reply)

    async def handle_stream_connect(self, results):
        self.send_socks_connect_reply(results)
        await self.stream_clients[results['client_id']].connect()

    async def handle_stream_disconnect(self, results):
        self.send_socks_connect_reply(results)
        self.stream_clients[results['client_id']].client_socket.close()
        del self.stream_clients

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
