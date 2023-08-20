import os
import socket
import select
import datetime
import json
import threading
from collections import namedtuple
from connect.output import display
from connect.convert import bytes_to_base64, base64_to_string, base64_to_bytes
from connect.generate import string_identifier, digit_identifier
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


class SocksClient:
    SOCKS_VERSION = 5
    stream = True
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

    def __init__(self, agent, client, database_session):
        self.agent = agent
        self.client = client
        self.database_session = database_session
        self.client_id = string_identifier()
        self.atype_functions = {
            b'\x01': self._parse_ipv4_address
            # 3: self._parse_domain_name,
            # 4: self._parse_ipv6_address
        }

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

    def parse_address(self):
        atype = self.client.recv(1)
        try:
            address, port = self.atype_functions.get(atype)(), int.from_bytes(self.client.recv(2), 'big', signed=False)
            return atype, address, port
        except:
            self.client.sendall(self.generate_reply(atype, 8, None, None))
            return None, None, None

    def _parse_ipv4_address(self):
        return socket.inet_ntoa(self.client.recv(4))

    def proxy(self):
        if not self.negotiate_method():
            display('Socks client failed to negotiate method.', 'ERROR')
            self.client.close()
            return
        if not self.negotiate_cmd():
            display('Socks client failed to negotiate cmd.', 'ERROR')
            self.client.close()
            return
        atype, address, port = self.parse_address()
        if not address:
            display('Socks client failed to negotiate address.', 'ERROR')
            self.client.close()
            return
        self.create_new_task(
            method='socks_connect',
            task_type=2,
            parameters=[
                str(address),
                str(port),
                self.client_id,
            ])

    def upstream(self, upstream_data):
        upstream_data = bytes_to_base64(upstream_data)
        self.create_new_task(method='socks_upstream',
                             task_type=2,
                             parameters=[
                                 self.client_id,
                                 upstream_data
                             ])

    def generate_reply(self, rep, address, port):
        print(f"generating_reply: {','.join([str(rep), address, str(port)])}")
        return b''.join([
            self.SOCKS_VERSION.to_bytes(1, 'big'),
            int(rep).to_bytes(1, 'big'),
            int(0).to_bytes(1, 'big'),
            int(1).to_bytes(length=1, byteorder='big'),
            socket.inet_aton(address) if address else int(0).to_bytes(1, 'big'),
            port.to_bytes(2, 'big') if port else int(0).to_bytes(1, 'big')
        ])

    def handle_socks_connect_results(self, results):
        rep = int(results['rep'])
        bind_addr = results['bind_addr'] if results['bind_addr'] else None
        bind_port = int(results['bind_port']) if results['bind_port'] else None
        try:
            self.client.sendall(self.generate_reply(rep, bind_addr, bind_port))
        except socket.error as e:
            print("Could not send sock_connect:", e)
            return
        while True:
            r, w, e = select.select([self.client], [], [], 1)

            if self.client in r:
                print('reading')
                data = self.client.recv(4096)
                if len(data) == 0:
                    break
                self.upstream(data)

    def handle_socks_downstream_results(self, results):
        downstream_data = base64_to_bytes(results['downstream_data'])
        print(downstream_data)
        try:
            self.client.sendall(downstream_data)
        except:
            print('failed to send downstream')

    def create_new_task(self, method, task_type, parameters=None, misc=None):
        new_task_query = text(
            """
            INSERT INTO task_model (id, created, method, type, _parameters, _misc, agent_id)
            VALUES (:id, :created, :method, :type, :parameters, :misc, :agent_id)
            """
        )
        # if parameters:
        #     for parameter in parameters:
        #         parameter[]
        params = {
            'id': digit_identifier(),
            'created': datetime.datetime.now(),
            'method': method,
            'type': task_type,
            'parameters': ','.join(parameters) if parameters else '',
            'misc': ','.join(misc) if misc else '',
            'agent_id': self.agent,
        }

        self.database_session.execute(new_task_query, params)
        self.database_session.commit()


class SocksServer:
    proxy = True
    socks_client = namedtuple('SocksClient', ['thread', 'socks_client'])
    socks_clients = []

    def __init__(self, address, port, agent, database_session):
        self.address = address
        self.port = port
        self.agent = agent
        self.database_session = database_session

    def listen_for_clients(self):
        socks_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socks_server.bind((self.address, self.port))
        socks_server.settimeout(1.0)
        socks_server.listen(5)
        while self.proxy:
            try:
                client, addr = socks_server.accept()
            except:
                continue
            #client.settimeout(5.0)
            socks_client = SocksClient(self.agent, client, self.database_session)
            socks_client_thread = threading.Thread(target=socks_client.proxy)
            socks_client_thread.daemon = True
            socks_client_thread.start()
            self.socks_clients.append(self.socks_client(socks_client_thread, socks_client))
        socks_server.close()

    def shutdown(self):
        for socks_client in self.socks_clients:
            socks_client.socks_client.stream = False
            socks_client.thread.join()
        self.proxy = False


class SocksManager:
    socks_server = namedtuple('SocksServer', ['thread', 'socks_server'])
    socks_servers = {}

    def __init__(self):
        engine = create_engine(f'sqlite:///{os.getcwd()}/instance/connect.db')
        self.session = sessionmaker(bind=engine)()

    def create_socks_server(self, *args):
        new_socks_server = SocksServer(*args, self.session)
        socks_server_thread = threading.Thread(target=new_socks_server.listen_for_clients)
        socks_server_thread.daemon = True
        socks_server_thread.start()
        self.socks_servers[args[2]] = self.socks_server(socks_server_thread, new_socks_server)
        display(f'Successfully created socks server: {args[0]}:{str(args[1])}', 'SUCCESS')

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
        print(base64_to_string(results))
        results = json.loads(base64_to_string(results))
        for socks_server in self.socks_servers.values():
            for socks_client in socks_server.socks_server.socks_clients:
                if socks_client.socks_client.client_id == results['client_id']:
                    if method == 'socks_connect':
                        socks_client.socks_client.handle_socks_connect_results(results)
                    if method == 'socks_downstream':
                        socks_client.socks_client.handle_socks_downstream_results(results)
