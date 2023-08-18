import json
from functools import wraps
from flask_socketio import disconnect
from connect.server.models import AgentModel, db, ImplantModel, TaskModel


class TeamServerEvents:

    def __init__(self, key, team_server_sio):
        self.key = key
        self.team_server_sio = team_server_sio
        self.team_server_sio.on_event('agent', self.agent)
        self.team_server_sio.on_event('connect', self.connect)
        self.team_server_sio.on_event('implant', self.implant)
        self.team_server_sio.on_event('task', self.task)

    def connect(self, auth: str == ''):
        if auth != self.key:
            disconnect()

    # JSON event handler decorator
    def json_event_handler(handler_function):
        @wraps(handler_function)
        def decorated_handler(self, *args):
            if not args:
                self.team_server_sio.emit('error', f'No data provided to {handler_function.__name__}.')
                return
            try:
                deserialized_json = json.loads(args[0])
            except json.JSONDecodeError:
                self.team_server_sio.emit('error', f'Invalid JSON provided to {handler_function.__name__} event: {args[0]}')
                return
            return handler_function(self, deserialized_json)

        return decorated_handler

    @json_event_handler
    def agent(self, data):
        list_agent = 'list' in data.keys()
        if list_agent:
            agents = [agent.get_agent() for agent in AgentModel.query.all()]
            if not agents:
                self.team_server_sio.emit('information', 'There are no agents.')
                return
            table = self.create_table('AGENTS', agents[0].keys(), agents)
            self.team_server_sio.emit('default', table)
            return
        self.team_server_sio.emit('information', f'Agent event hit with the following data: {data}')



    # Event handler for implant actions
    @json_event_handler
    def implant(self, data):
        create_implant = 'create' in data.keys()
        list_implant = 'list' in data.keys()
        if create_implant:
            new_implant = ImplantModel()
            self.commit(new_implant)
            self.team_server_sio.emit('success', f'Implant `{new_implant.id}` created their key is: `{new_implant.key}`')
            return
        if list_implant:
            implants = [implant.get_implant() for implant in ImplantModel.query.all()]
            if not implants:
                self.team_server_sio.emit('information', 'There are no implants.')
                return
            table = self.create_table('IMPLANTS', implants[0].keys(), implants)
            self.team_server_sio.emit('default', table)
            return
        self.team_server_sio.emit('information', f'Implant event hit with the following data: {data}')

    # Event handler for task actions
    @json_event_handler
    def task(self, data):
        create_task = data.get('create')
        if create_task:
            agent = AgentModel.query.filter_by(id=create_task['agent']).first()
            parameters = ','.join(create_task.get('parameters', []))
            new_task = TaskModel(agent=agent, method=create_task['method'], type=create_task['type'],
                                 parameters=parameters)
            self.commit(new_task)
            self.team_server_sio.emit('success', f'Scheduled task for method: `{new_task.method}`')
            return
        self.team_server_sio.emit('information', f'Task event hit with the following data: {data}')

    # Database utility function
    @staticmethod
    def commit(model):
        db.session.add(model)
        db.session.commit()

    # Calculate the length of the longest value in a list of dictionaries
    @staticmethod
    def longest_value(items: list[dict]):
        return max(len(value) for item in items for value in item.values())

    # Generate a formatted table output
    def create_table(self, title, columns: list, items: list[dict]) -> str:
        # ToDo: Pretty sure this logic is faulty if a column name is longer then one of the values. But meh.
        column_length = self.longest_value(items)
        title_padding = int(column_length / 2) * int(len(columns) / 2)
        table_output = f'{" " * title_padding}{title.upper()}\n'
        table_output += ' '.join('{:<{}}'.format(column, column_length) for column in columns) + '\n'
        table_seperator = '•' * column_length
        table_output += f'{table_seperator} ' * len(columns) + ' \n'
        table_output += '\n'.join(
            ' '.join('{:<{}}'.format(item[column], column_length) for column in columns) for item in items)
        return table_output
