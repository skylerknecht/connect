import json
import socketio

sio = socketio.Client()
sio.connect('http://127.0.0.1:8081/')
sio.emit('implant', json.dumps({'create': None}))

@sio.event
def information(data):
    print(data)
