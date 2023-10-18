from .commands import ConnectCommand


class Streamers(ConnectCommand):
    def __init__(self):
        super().__init__(
            'streamers',
            'Start a stream server.',
            parameters={
                'ip': 'What IP to bind to',
                'port': 'What Port to bind to',
            }
        )

    def execute_command(self, parameters, client_sio):
        if len(parameters) == 0:
            client_sio.emit('streamer', {'list': None})
            return
        switch = parameters[0]
        if switch == 'add':
            stream_task = {
                'create': {
                    'type': parameters[1],
                    'agent_id': parameters[2],
                    'ip': parameters[3],
                    'port': parameters[4],
                }
            }
            client_sio.emit('streamer', stream_task)
