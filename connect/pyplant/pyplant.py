import argparse
import json
import random
import requests
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
                print(task)

    def setup_parser(self, subparser):
        parser = subparser.add_parser(self.NAME, help='Python Implant for debugging.',
                                      formatter_class=argparse.RawTextHelpFormatter, usage=argparse.SUPPRESS)
        parser.add_argument('url', metavar='url', help='Listener URL.')
        parser.add_argument('key', metavar='key', help='Implant Key.')
        parser.add_argument('--debug', action='store_true', help='Enable debug mode.')

    @staticmethod
    def verify_task_format(task: dict) -> bool:
        return True

