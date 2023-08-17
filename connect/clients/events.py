import json
import socketio


class Events:
    sio = socketio.Client()

    def __init__(self, notify):
        self.notify = notify
        self.sio.on('default', self.default)
        self.sio.on('error', self.error)
        self.sio.on('information', self.information)
        self.sio.on('success', self.success)

    def default(self, data):
        self.notify(data, 'DEFAULT')

    def error(self, data):
        self.notify(data, 'ERROR')

    def information(self, data):
        self.notify(data, 'INFORMATION')

    def success(self, data):
        self.notify(data, 'SUCCESS')


