import socketio

sio = socketio.Client()
sio.connect('http://127.0.0.1:8080')
sio.emit('listener', 'lol')
