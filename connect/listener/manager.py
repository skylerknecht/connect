import threading
from .listener import ConnectListener
from connect.server.models import Session


class ListenerManager:

    def __init__(self):
        self.listeners = []

    def create_listener(self, team_server_uri, team_server_key, ip, port):
        listener = ConnectListener(Session())
        thread = threading.Thread(target=listener.run, daemon=True, args=(team_server_uri, team_server_key, ip, port,))
        thread.start()
        self.listeners.append([listener, thread])