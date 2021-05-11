import socket

from connect import color

class Server:

    data = b''

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.create_socket()

    def create_socket(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind((self.ip, int(self.port)))
        color.success(f'Socket successfully created. ({self.ip}:{self.port})')
        return 0

    def receive_data(self):
        self.data = self.data + self.server.recv(60000)
        return 0

    def data_size(self):
        color.normal(len(self.data))
        return 0

class Ingestor:

    def __init__(self, data, name):
        self.data = data
        self.name = name

    def __str__(self):
        color.normal(f'{self.name} : {len(self.data)}')

class DiscordIngestor(Ingestor):
    pass
