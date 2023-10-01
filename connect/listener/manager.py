import threading
from .listener import ConnectListener
from connect.generate import string_identifier


class ListenerManager:

    def __init__(self):
        self.listeners = {}

    def create_listener(self, team_server_uri, team_server_key, ip, port):
        listener = ConnectListener(ip, port)
        thread = threading.Thread(target=listener.run, daemon=True, args=(team_server_uri, team_server_key))
        thread.start()
        self.listeners[string_identifier()] = [listener, thread]

    def get_listeners(self):
        listeners = []
        for identifier, listener in self.listeners.items():
            listener = listener[0]
            listeners.append({
                'id': identifier,
                'ip': listener.ip,
                'port': listener.port
            })
        return listeners

    def shutdown_listener(self, id):
        if not id in self.listeners.keys():
            return False
