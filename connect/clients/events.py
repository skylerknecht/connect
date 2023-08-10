import socketio

sio = socketio.Client()


@sio.event
def output(data):
    print(data)