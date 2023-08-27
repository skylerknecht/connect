import datetime
import select
import socket
import time

from collections import namedtuple
from connect import get_debug_level
from connect.output import display
from connect.convert import bytes_to_base64, base64_to_bytes
from connect.generate import string_identifier, digit_identifier
from sqlalchemy import text


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

    def __init__(self, agent_id, client, database_session):
        self.agent_id = agent_id
        self.atype_functions = {
            b'\x01': self._parse_ipv4_address,
            b'\x03': self._parse_domain_name,
            b'\x04': self._parse_ipv6_address
        }
        self.client = client
        self.client_id = string_identifier()
        self.database_session = database_session
        self.downstream_buffer = []
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
        ver, nmethods = self.client.recv(2)

        methods = [ord(self.client.recv(1)) for _ in range(nmethods)]
        if 0 not in methods:
            self.client.sendall(bytes([self.SOCKS_VERSION, int('FF', 16)]))
            return False

        self.client.sendall(bytes([self.SOCKS_VERSION, 0]))
        return True

    def parse_socks_connect(self):
        if not self.negotiate_method():
            display(f'Client {self.client_id} failed to negotiate method.', 'ERROR')
            self.client.close()
            return
        if not self.negotiate_cmd():
            display(f'Client {self.client_id} failed to negotiate cmd.', 'ERROR')
            self.client.close()
            return
        atype, address, port = self.parse_address()
        if not address:
            display(f'Client {self.client_id} failed to negotiate address.', 'ERROR')
            self.client.close()
            return
        if get_debug_level() >= 1: display(f'Client {self.client_id} sent socks_connect request for {address}:{str(port)}'
                                         , 'INFORMATION')
        atype = int.from_bytes(atype, byteorder='big')
        self.create_new_task('socks_connect', parameters=[str(atype), address, str(port), self.client_id])

    def upstream(self, upstream_data):
        upstream_data = bytes_to_base64(upstream_data)
        self.create_new_task(method='socks_upstream',
                             parameters=[
                                 self.client_id,
                                 upstream_data
                             ],
                             delete_on_send=True)

    def stream(self):
        self.streaming = True
        if get_debug_level() >= 1: display(f'Client {self.client_id} is streaming', 'INFORMATION')
        while self.streaming:
            time.sleep(0.1)
            r, w, e = select.select([self.client], [self.client], [])
            if self.client in w and len(self.downstream_buffer) > 0:
                self.client.send(self.downstream_buffer.pop(0))
                continue
            if self.client in r:
                try:
                    data = self.client.recv(4096)
                    if len(data) <= 0:
                        break
                    print(data)
                    self.upstream(data)
                except Exception:
                    break
        if get_debug_level() >= 1: display(f'Client {self.client_id} stopped streaming', 'INFORMATION')
        self.streaming = False
        self.client.close()

    def handle_socks_connect_results(self, results):
        atype = results['atype']
        rep = results['rep']
        bind_addr = results['bind_addr'] if results['bind_addr'] else None
        bind_port = int(results['bind_port']) if results['bind_port'] else None
        if get_debug_level() >= 1: display(f'Client {self.client_id} received socks_connect reply: {results}', 'INFORMATION')
        try:
            self.client.sendall(self.generate_reply(atype, rep, bind_addr, bind_port))
            if get_debug_level() >= 1: display(f'Client {self.client_id} sent socks_connect', 'SUCCESS')
        except socket.error as e:
            if get_debug_level() >= 1: display(f'Client {self.client_id} could not send sock_connect: {e}', 'ERROR')
            return
        if not bind_addr:
            return
        self.stream()

    def handle_socks_downstream_results(self, results):
        if get_debug_level() >= 2: display('Received downstream results', 'INFORMATION')
        try:
            data = base64_to_bytes(results['data'])
            if len(data) == 0:
                return
            self.downstream_buffer.append(data)
        except socket.error as e:
            if get_debug_level() >= 1: display(f"Failed to send downstream results {e}", 'ERROR')
            return

    def create_new_task(self, method, parameters=None, delete_on_send=False):
        new_task_query = text("""
            INSERT INTO task_model (id, created, method, type, _parameters, _misc, delete_on_send, agent_id)
            VALUES (:id, :created, :method, :type, :parameters, :misc, :delete_on_send, :agent_id)
            """)

        params = {
            'id': digit_identifier(),
            'created': datetime.datetime.now(),
            'method': method,
            'type': 2,
            'parameters': ','.join(parameters) if parameters else '',
            'misc': '',
            'delete_on_send': delete_on_send,
            'agent_id': self.agent_id
        }

        self.database_session.execute(new_task_query, params)
        self.database_session.commit()


class SocksServer:
    proxy = True
    socks_client = namedtuple('SocksClient', ['thread', 'socks_client'])
    socks_clients = []

    def __init__(self, address, port, agent_id, database_session):
        self.address = address
        self.port = port
        self.agent_id = agent_id
        self.database_session = database_session

    def listen_for_clients(self):
        socks_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            socks_server.bind((self.address, self.port))
            display(f'Agent {self.agent_id} is listening on {self.address}:{self.port}', 'SUCCESS')
        except Exception as e:
            display(f'Failed to start socks server {e}', 'ERROR')
            self.proxy = False
            return
        socks_server.settimeout(1.0)
        socks_server.listen(5)
        while self.proxy:
            try:
                client, addr = socks_server.accept()
            except:
                continue
            socks_client = SocksClient(self.agent_id, client, self.database_session)
            socks_client.parse_socks_connect()
            self.socks_clients.append(socks_client)
        socks_server.close()

    def shutdown(self):
        for socks_client in self.socks_clients:
            socks_client.stream = False
        self.proxy = False
