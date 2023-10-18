import asyncio
import json
import select

from connect.convert import string_to_base64, bytes_to_base64


class StreamClient:

    def __init__(self, agent_id, client_socket):
        self.agent_id = agent_id
        self.client_socket = client_socket
        self.downstream_buffer = []
        self.upstream_buffer = []
        self.connected = True
        self._seqno = 0

    @property
    def seqno(self):
        self._seqno += 1
        return self._seqno

    async def connect(self):
        while self.connected:
            read, write, execute = select.select([self.client_socket], [self.client_socket], [])
            if self.client_socket in write and len(self.downstream_buffer) > 0:
                data = self.downstream_buffer.pop(0)
                try:
                    self.client_socket.send(data)
                except OSError:
                    break
                continue
            if self.client_socket in read:
                try:
                    data = self.client_socket.recv(4096)
                    self.create_upstream_task(data)
                except OSError:
                    break
            await asyncio.sleep(0.1)
        self.client_socket.close()

    def create_upstream_task(self, data):
        self.upstream_buffer.append(json.dumps({
            'data': bytes_to_base64(data),
            'client_id': id(self.client_socket)
        }))
