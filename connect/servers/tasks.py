import datetime

from .models import AgentModel, ImplantModel, TaskModel
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


class ResultsHandler:

    def __init__(self):
        self.task_types = {
            0: self.process_string_results,
            1: self.process_file_results
        }

    def process_results(self, task, results):
        self.task_types[task.type](task, results)

    def process_string_results(self, task, results):
        print(results)

    def process_file_results(self, task, results):
        print(results)


class TaskManager:
    def __init__(self):
        self.incoming_tasks = {}
        self.results_handler = ResultsHandler()

    def parse_batch_response(self, batch_response: list) -> list:
        batch_request = []
        for task in batch_response:
            #ToDo: Verify JSON_RPC 2.0 compliance of `task`
            task_id = next((v for k, v in task.items() if k.lower() == 'id'), None)
            result = next((v for k, v in task.items() if k.lower() == 'result'), None)
            error = next((v for k, v in task.items() if k.lower() == 'error'), None)
            agent = AgentModel.query.filter_by(check_in_task_id=task_id)
            if agent:
                batch_request = agent.get_tasks()
                continue
            task = TaskModel.query.filter_by(id=task_id)
            if not task:
                print(f'Failed to find task with id {task_id}')
                continue
            if result:
                self.incoming_tasks[task] = result
                continue
            if error:
                print(error['message'])
                continue
        return batch_request

    def parse_results(self):
        while True:
            for task, result in self.incoming_tasks.items():
                task.completed = datetime.datetime.now()
                self.results_handler.process_results(task, result)
