import socket
import socketio
import threading

from collections import namedtuple

class Proxy:

    SOCKS_VERSION = 5
    PACKET_SIZE = 266

    def __init__(self):#, team_server_uri, key):
        #self.sio_client = socketio.Client(ssl_verify=False, logger=False)
        #self.sio_client.connect(team_server_uri, auth=key)
        pass

    def generate_reply(self, atype, rep):
        return b''.join([
            self.SOCKS_VERSION.to_bytes(1, 'big'), 
            int(rep).to_bytes(1, 'big'), 
            int(0).to_bytes(1, 'big'),
            int(atype).to_bytes(1, 'big'), 
            int(0).to_bytes(1, 'big'), # ToDo: don't know how to get the address from the client connected to yet..
            int(0).to_bytes(1, 'big') # ToDo: don't know how to get the port from the client connection
        ])

    def handle_client(self, conn):
        ver, nmethods = conn.recv(2)

        methods = [ord(conn.recv(1)) for _ in range(nmethods)]

        if 0 not in methods:
            conn.sendall(bytes([self.SOCKS_VERSION, int('FF', 16)]))
            return
        
        conn.sendall(bytes([self.SOCKS_VERSION, 0]))

        self.handle_requests(conn)

    def handle_requests(self, conn):

        atype_functions = { 
            1: self.parse_ipv4_address,
            3: self.parse_domain_name,
            4: self.parse_ipv6_address
        }

        _, cmd, _, atype = conn.recv(4) # ToDo: ver and rsv not used

        address = atype_functions.get(atype)(conn)

        port = int.from_bytes(conn.recv(2), 'big', signed=False)

        if cmd != 0:
            print(self.generate_reply(atype, 7))
            conn.sendall(self.generate_reply(atype, 7))


    def run(self, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.listen()

        while True:            
            print('SOCKS5 server listening on {}:{}'.format(*s.getsockname()))
            conn, addr = s.accept()
            print('New connection from {}:{}'.format(*addr))           
            t = threading.Thread(target=self.handle_client, args=(conn,))
            t.daemon = True
            t.start()

    def parse_ipv4_address(self, conn):
        return socket.inet_ntoa(conn.recv(4))

    def parse_domain_name(self, conn):
        return conn.recv(conn.recv(1)[0])

    def parse_ipv6_address(self, conn):
        return socket.inet_ntop(socket.AF_INET6, conn.recv(16))