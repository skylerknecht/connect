import select
import socket
import socketio
import threading

class Proxy:

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

    def __init__(self):
        pass

    def generate_reply(self, atype, rep, address, port):
        return b''.join([
            self.SOCKS_VERSION.to_bytes(1, 'big'), 
            int(rep).to_bytes(1, 'big'), 
            int(0).to_bytes(1, 'big'),
            int(atype).to_bytes(1, 'big'), 
            socket.inet_aton(address) if address else int(0).to_bytes(1, 'big'),
            port.to_bytes(2, 'big') if port else int(0).to_bytes(1, 'big')
        ])

    def handle_client(self, conn):
        ver, nmethods = conn.recv(2)

        methods = [ord(conn.recv(1)) for _ in range(nmethods)]

        if 0 not in methods:
            conn.sendall(bytes([self.SOCKS_VERSION, int('FF', 16)]))
            conn.close()
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
        rep = 0 # Default to succeed unless otherwise set

        try:
            address = atype_functions.get(atype)(conn)
        except:
            conn.sendall(self.generate_reply(atype, 8, None, None))
            conn.close()
            return

        port = int.from_bytes(conn.recv(2), 'big', signed=False)

        if cmd != 1:
            conn.sendall(self.generate_reply(atype, 7, None, None))
            conn.close()
            return

        remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
        try:
            remote.connect((address, port))
        except socket.timeout:
            rep = 4
        except Exception:
            rep = 1
        
        if rep != 0:
            #print(self.REPLIES[rep])
            conn.sendall(self.generate_reply(atype, rep, None, None))
            conn.close()
            return

        conn.sendall(self.generate_reply(atype, rep, remote.getsockname()[0], remote.getsockname()[1]))

        while True:
            r, w, e = select.select([conn, remote], [], []) 

            if conn in r:
                data = conn.recv(4096)
                if remote.send(data) <= 0:
                    break

            if remote in r:
                data = remote.recv(4096)
                if conn.send(data) <= 0:
                    break

        remote.close()
        conn.close()

    def run(self, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.listen()
        print('SOCKS5 server listening on {}:{}'.format(*s.getsockname()))

        while True:            
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