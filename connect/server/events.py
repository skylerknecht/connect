import json

from . import models
from connect import generate
from flask_socketio import disconnect, SocketIO
from functools import wraps

KEY = generate.string_identifier(20)
sio = SocketIO()


def commit(model):
    models.db.session.add(model)
    models.db.session.commit()


@sio.event
def connect(auth: str == ''):
    if not auth == KEY:
        disconnect()


def json_rpc_event_handler(handler_function):
    @sio.on(handler_function.__name__)
    @wraps(handler_function)
    def decorated_handler(*args):
        if len(args) < 1:
            print(f'No data provided to {handler_function.__name__}.')
            return
        try:
            decoded_data = json.loads(args[0])
        except json.JSONDecodeError:
            print(f'Invalid JSON provided to {handler_function.__name__} event: {args[0]}')
            return
        return handler_function(decoded_data)
    return decorated_handler


@json_rpc_event_handler
def listener(data):
    create = data.get('create') if 'create' in data.keys() else None
    if create:
        pass
