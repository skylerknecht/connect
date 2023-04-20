import abc
import json
import socket
import socketio
import select
import threading

from connect import output
from connect import convert

class ProxyClient(metaclass=abc.ABCMeta):

    SOCKS_VERSION = 5
    PACKET_SIZE = 266
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

    def __init__(self, client):
        self.client =  client
        self.atype_functions = { 
            b'\x01': self._parse_ipv4_address
            #3: self._parse_domain_name,
            #4: self._parse_ipv6_address
        }

    def generate_reply(self, atype, rep, address, port):
        return b''.join([
            self.SOCKS_VERSION.to_bytes(1, 'big'), 
            int(rep).to_bytes(1, 'big'), 
            int(0).to_bytes(1, 'big'),
            atype, 
            socket.inet_aton(address) if address else int(0).to_bytes(1, 'big'),
            port.to_bytes(2, 'big') if port else int(0).to_bytes(1, 'big')
        ])

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
    
    def _parse_domain_name(self):
        pass #ToDo 
    
    def _parse_ipv6_address(self):
        pass #ToDo
        #return socket.inet_ntop(socket.AF_INET6, self.client.recv(16))

    def run(self):
        if not self.negotiate_method():
            print('failed to negotite method')
            self.client.close()
            return
        if not self.negotiate_cmd():
            print('failed to negotite cmd')
            self.client.close()
            return
        atype, address, port = self.parse_address()        
        if not address:
            print('failed to parse address')
            self.client.close()
            return
        self.proxy(atype, address, port)

    @abc.abstractmethod
    def proxy(self, atype, address, port):
        pass


class RemoteProxyClient(ProxyClient):

    def __init__(self, client, team_server_uri, key, agent_id):
        super().__init__(client)
        self.agent_id = agent_id
        self.sio_client = socketio.Client(ssl_verify=False, logger=False)
        self.sio_client.connect(team_server_uri, auth=key)
        self.sio_client.on('socks_connect', self.socks_connect)
        self.sio_client.on(f'socks_downstream_{self.sio_client.sid}', self.downstream)

    def proxy(self, atype, address, port):
        args = [address, str(port), str(int.from_bytes(atype, byteorder='big'))]
        task = output.Task('socks_connect', 'SOCKS5 Connect', args, 0)
        self.sio_client.emit('task', f'{{"agent":"{self.agent_id}", "task": {json.dumps(task)}}}')
    
    def socks_connect(self, data):
        if not data:
            self.sio_client.emit('error', 'Socks reply event triggered with no data')
            return
        
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            self.sio_client.emit('error', 'Invalid JSON provided to socks reply event')
            return
        
        try:
            remote = data.get('remote')
            rep = int(data.get('rep'))
            atype = int(data.get('atype')).to_bytes(length=1, byteorder='big')
            bind_addr = data.get('bind_addr')
            bind_port = int(data.get('bind_port'))
        except:
            self.client.sendall(self.generate_reply(atype, 1, None, None))
            self.sio_client.emit('error', 'Invalid JSON provided to socks reply event')
            return

        if rep != 0:
            print(self.REPLIES[rep])
            self.client.sendall(self.generate_reply(atype, rep, None, None))
            self.client.close()
            return

        self.client.sendall(self.generate_reply(atype, rep, bind_addr, bind_port))
        self.socks_stream(remote)

    def socks_stream(self, remote):
        while True:
            r, w, e = select.select([self.client], [], []) 

            if self.client in r:
                self.upstream(remote, self.client.recv(4096))

            args = [remote, self.sio_client.sid]
            task = output.Task('socks_downstream', 'SOCKS5 TCP DOWNSTREAM', args, 0)
            self.sio_client.emit('task', f'{{"agent":"{self.agent_id}", "task": {json.dumps(task)}}}')

        remote.close()
        self.client.close()

    def upstream(self, remote, upstream_data):
        upstream_data = convert.bytes_to_base64(upstream_data)    
        args = [remote, upstream_data]
        task = output.Task('socks_upstream', 'SOCKS5 TCP UPSTREAM', args, 0)
        self.sio_client.emit('task', f'{{"agent":"{self.agent_id}", "task": {json.dumps(task)}}}')

    def downstream(self, data):
        data = json.loads(data)
        downstream_data = convert.base64_to_bytes(data.get('downstream_data'))
        self.client.send(downstream_data)

    def socks_stream_read(self, remote):
        while True:
            r, w, e = select.select([self.client], [self.client], [])
            print('waiting for upstream..')
            if r:
                print('upstream ▼--------------------------▼')
                upstream_data = self.client.recv(500000)
                if len(upstream_data) <= 0:
                    print('no data')
                    print('upstream ▲--------------------------▲')
                    continue               
                upstream_data = convert.bytes_to_base64(upstream_data)    
                args = [remote, self.sio_client.sid, upstream_data]
                task = output.Task('socks_tcp_stream', 'SOCKS5 TCP STREAM', args, 0)
                self.sio_client.emit('task', f'{{"agent":"{self.agent_id}", "task": {json.dumps(task)}}}')
                print('upstream ▲--------------------------▲')
        # while True:
        #     r, w, e = select.select([self.client], [self.client], [])
        #     if r:
        #         print('reading upstream')
        #         upstream_data = self.client.recv(4096)
        #         if len(upstream_data) <= 0:
        #             continue
        #         print('upstream ▼--------------------------▼')
        #         print(upstream_data)
        #         upstream_data = convert.bytes_to_base64(upstream_data)    
        #         args = [remote, self.sio_client.sid, upstream_data]
        #         task = output.Task('socks_tcp_stream', 'SOCKS5 TCP STREAM', args, 0)
        #         self.sio_client.emit('task', f'{{"agent":"{self.agent_id}", "task": {json.dumps(task)}}}')
        #         print('upstream ▲--------------------------▲')
                
    def socks_stream_write(self, data):
        data = json.loads(data)
        downstream_data = convert.base64_to_bytes(data.get('downstream'))
        while True:
            r, w, e = select.select([self.client], [self.client], [])
            print('waiting for downstream..')
            if w:
                print('downstream ▼--------------------------▼')
                print(downstream_data)
                self.client.sendall(downstream_data)
                print('downstream ▲--------------------------▲')
                break



class LocalProxyClient(ProxyClient):

    def __init__(self, client):
        super().__init__(client)

    def proxy(self, atype, address, port):
        self.socks_connect(atype, address, port)

    def socks_connect(self, atype, address, port):
        remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
        try:
            remote.connect((address, port))
            rep = 0
        except socket.timeout:
            rep = 4
        except Exception:
            rep = 1
        
        if rep != 0:
            print(self.REPLIES[rep])
            self.client.sendall(self.generate_reply(atype, rep, None, None))
            self.client.close()
            return

        self.client.sendall(self.generate_reply(atype, rep, remote.getsockname()[0], remote.getsockname()[1]))
        self.socks_stream(remote)

    def socks_stream(self, remote):
        while True:
            r, w, e = select.select([self.client, remote], [], []) 

            if self.client in r:
                data = self.client.recv(4096)
                if remote.send(data) <= 0:
                    break

            if remote in r:
                data = remote.recv(4096)
                if self.client.send(data) <= 0:
                    break

        remote.close()
        self.client.close()

class Proxy:
 
    def __init__(self, address, port, remote=None):
        self.address = address
        self.port = port
        self.remote = remote

    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.address, self.port))
        server.listen()
        self.listen_for_clients(server)

    def listen_for_clients(self, server):
        print('SOCKS5 server listening for clients on {}:{}.'.format(*server.getsockname()))
        while True:
            client, addr = server.accept()
            print('New connection from {}:{}, creating proxy client.'.format(*addr))
            if self.remote:
                proxy_client = RemoteProxyClient(client, self.remote[0], self.remote[1], self.remote[2])
            else: 
                proxy_client = LocalProxyClient(client)
            t = threading.Thread(target=proxy_client.run)
            t.daemon = True
            t.start()