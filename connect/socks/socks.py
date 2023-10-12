import asyncio
import json
import select
import socket
import time

from collections import namedtuple
from connect import get_debug_level
from connect.convert import bytes_to_base64, base64_to_bytes
from connect.generate import string_identifier
from connect.output import display


class SocksClient:
    REPLIES = {
        0: 'succeeded',
        1: 'general SOCKS server failure',
        2: 'connection not allowed by ruleset',
        3: 'Network unreachable',
        4: 'Host unreachable',
        5: 'Connection refused',
        6: 'TTL expired',
        7: 'Command not supported',
        8: 'Address type not supported',
        **{i: 'unassigned' for i in range(9, 256)}
    }
    SOCKS_VERSION = 5

    def __init__(self, client):
        self.atype_functions = {
            b'\x01': self._parse_ipv4_address,
            b'\x03': self._parse_domain_name,
            b'\x04': self._parse_ipv6_address
        }
        self.client = client
        self.client_id = string_identifier()
        self.downstream_buffer = []
        self.socks_connect_sent = None
        self.socks_task = namedtuple('SocksTask', ['event', 'data'])
        self.socks_tasks = []
        self.streaming = False

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

    def parse_address(self):
        atype = self.client.recv(1)
        try:
            address, port = self.atype_functions.get(atype)(), int.from_bytes(self.client.recv(2), 'big', signed=False)
            return atype, address, port
        except KeyError:
            self.client.sendall(self.generate_reply(str(int.from_bytes(atype, byteorder='big')), 8, None, None))
            return None, None, None

    def _parse_ipv4_address(self):
        return socket.inet_ntoa(self.client.recv(4))

    def _parse_ipv6_address(self):
        ipv6_address = self.client.recv(16)
        return socket.inet_ntop(socket.AF_INET6, ipv6_address)

    def _parse_domain_name(self):
        domain_length = self.client.recv(1)[0]
        domain_name = self.client.recv(domain_length).decode('utf-8')
        return domain_name

    def negotiate_cmd(self):
        ver, cmd, rsv = self.client.recv(3)
        return cmd == 1

    def negotiate_method(self):
        try:
            ver, nmethods = self.client.recv(2)
        except Exception:
            return False
        methods = [ord(self.client.recv(1)) for _ in range(nmethods)]
        if 0 not in methods:
            self.client.sendall(bytes([self.SOCKS_VERSION, int('FF', 16)]))
            return False

        self.client.sendall(bytes([self.SOCKS_VERSION, 0]))
        return True

    def parse_socks_connect(self):
        if not self.negotiate_method():
            display(f"Client {self.client_id} failed to negotiate method.", "ERROR")
            self.client.close()
            return
        if not self.negotiate_cmd():
            display(f"Client {self.client_id} failed to negotiate cmd.", "ERROR")
            self.client.close()
            return
        atype, address, port = self.parse_address()
        if not address:
            display("Client {self.client_id} failed to negotiate address.", "ERROR")
            self.client.close()
            return
        data = json.dumps({
            'atype': int.from_bytes(atype, byteorder='big'),
            'address': address,
            'port': port,
            'client_id': self.client_id
        })
        if get_debug_level() >= 1:
            display(f"Client {self.client_id} scheduled socks_connect request for {address}:{str(port)}", "INFORMATION")
        if get_debug_level() >= 2:
            display(data)
        self.socks_tasks.append(self.socks_task('socks_connect', data))
        self.socks_connect_sent = time.time()

    def stream(self):
        self.streaming = True
        if get_debug_level() >= 1:
            display(f"Client {self.client_id} is streaming", "INFORMATION")
        while self.streaming:
            r, w, e = select.select([self.client], [self.client], [])
            if self.client in w and len(self.downstream_buffer) > 0:
                data = self.downstream_buffer.pop(0)
                self.client.send(data)
                if get_debug_level() >= 3:
                    display(f"Client {self.client_id} sent a {len(data)} byte downstream", "SUCCESS")
                if get_debug_level() >= 4: display(data)
                continue
            if self.client in r:
                try:
                    data = self.client.recv(4096)
                    if len(data) <= 0:
                        break
                    socks_upstream_task = json.dumps({
                        'client_id': self.client_id,
                        'data': bytes_to_base64(data)
                    })
                    self.socks_tasks.append(self.socks_task('socks_upstream', socks_upstream_task))
                    if get_debug_level() >= 3:
                        display(f"Client {self.client_id} scheduled a {len(data)} byte upstream", "INFORMATION")
                    if get_debug_level() >= 4: display(data)
                except Exception as e:
                    break
        if get_debug_level() >= 1:
            display(f"Client {self.client_id} stopped streaming", "INFORMATION")
        self.streaming = False
        self.client.close()

    def handle_socks_connect_results(self, results):
        atype = 1  # Unsure if this is the atype that we binded to or that we used
        rep = results['rep']
        bind_addr = results['bind_addr'] if results['bind_addr'] else None
        bind_port = int(results['bind_port']) if results['bind_port'] else None
        if get_debug_level() >= 2:
            display(f"Client {self.client_id} received socks_connect reply: {results}", "INFORMATION")
        try:
            self.client.sendall(self.generate_reply(atype, rep, bind_addr, bind_port))
            if get_debug_level() >= 1:
                display(f"Client {self.client_id} sent socks_connect", "SUCCESS")
        except socket.error as e:
            if get_debug_level() >= 1:
                display(f"Client {self.client_id} could not send sock_connect: {e}", "ERROR")
            return
        if not bind_addr:
            self.client.close()
            return
        network_delay = time.time() - self.socks_connect_sent
        if network_delay < 1:
            network_delay_notification = 'INFORMATION'
        else:
            network_delay_notification = 'WARN'
        display(f"The socks_connect network delay is {network_delay:.6f} seconds", network_delay_notification)
        self.stream()

    def handle_socks_downstream_results(self, results):
        try:
            data = base64_to_bytes(results['data'])
            if len(data) == 0:
                if get_debug_level() >= 1:
                    display(f"Client {results['client_id']} received an empty downstream", 'ERROR')
                return
            self.downstream_buffer.append(data)
            if get_debug_level() >= 3:
                display(f"Client {results['client_id']} received {len(data)} byte downstream.", 'INFORMATION')
        except Exception as e:
            if get_debug_level() >= 1:
                display(f"Client {results['client_id']} failed to schedule downstream {e}", 'ERROR')
            return


class SocksServer:
    listening = True
    socks_client = namedtuple('SocksClient', ['thread', 'socks_client'])

    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.socks_clients = []
        self.socks_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socks_server.bind((self.address, self.port))
        self.socks_server.settimeout(2.0)
        self.socks_server.listen(10)
        self.listening = True

    async def listen_for_clients(self):
        while self.listening:
            try:
                client, addr = await asyncio.to_thread(self.socks_server.accept)
            except socket.error:
                continue
            socks_client = SocksClient(client)
            self.socks_clients.append(socks_client)
            await asyncio.to_thread(socks_client.parse_socks_connect)
        self.socks_server.close()

    def shutdown(self):
        for socks_client in self.socks_clients:
            socks_client.streaming = False
        self.listening = False
