import socketio
import json
client_websocket = socketio.Client()
client_websocket.connect('http://192.168.1.23:8080/', auth='4666325248')

@client_websocket.event
def implant(data):
    print(data)

@client_websocket.event
def connected(data):
    print(data)

listener = {
    'listener_name': 'HTTP Listener',
    'ip': '192.168.1.23',
    'port': 9090
}
client_websocket.emit('listeners', json.dumps(listener))
implant = {
    'implant_name':'CSHARP_EXE',
    'language':'CSHARP'
}
client_websocket.emit('implants', json.dumps(implant))