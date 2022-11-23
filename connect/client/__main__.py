import argparse
import socketio
import json

from . import client
from . import command_sets
from connect.convert import base64_to_string
from connect.output import print_agents_table, print_stagers_table
from connect.output import print_success, print_info, print_error, print_traceback
from connect.output import Agent, Stager
from os import getcwd
from sys import exit
from time import sleep

client_websocket = socketio.Client()
connect_client = client.ConnectClient(allow_cli_args=False, shortcuts={'*': 'interact', '!': 'shell', '?': 'help -v'},
                                      persistent_history_file=f'{getcwd()}/.backup/command.history')


def post_task(task):
    task_json = f'{{"agent_name":"{connect_client.current_agent}",{task}}}'
    client_websocket.emit('new_task', task_json)


for command_set in command_sets.COMMAND_SETS:
    connect_client.register_command_set(command_set(post_task))

connect_client.disable_command_sets()


@client_websocket.event
def connected(data):
    _agent = Agent(*data['agent'])
    connect_client.agents.extend([_agent])
    print('\n')
    print_success(f'{_agent.name} is available.')


@client_websocket.event
def task_sent(data):
    print('\n')
    print_info(data)


@client_websocket.event
def task_results(data):
    data = json.loads(data)
    print('\n')
    print_success(data['banner'])
    print(base64_to_string(data['results']))


@client_websocket.event
def task_error(data):
    data = json.loads(data)
    print('\n')
    print_error(data['banner'])
    print(base64_to_string(data['results']))


@client_websocket.event
def agents(data):
    sleep(0.5)
    _agents = data['agents']
    for index, _agent in enumerate(_agents):
        _agents[index] = Agent(*_agent)
    connect_client.agents.extend(_agents)
    print_agents_table(_agents, connect_client.current_agent)


@client_websocket.event
def stagers(data):
    sleep(0.5)
    _stagers = data['stagers']
    _server_uri = data['server_uri']
    for index, _stager in enumerate(_stagers):
        _stagers[index] = Stager(*_stager)
    print_stagers_table(_stagers, _server_uri)


@client_websocket.event
def implants(data):
    print('\n')
    print_success(data)


def main():
    """
    The connect client controller.
    """

    parser = argparse.ArgumentParser('ConnectClient', 'Connect Client', conflict_handler='resolve')
    parser.add_argument('team_server_uri', help='Team Server\'s URI.')
    parser.add_argument('key', help='Team Server\'s Key.')
    args = parser.parse_args()
    try:
        client_websocket.connect(args.team_server_uri, auth=args.key)
    except socketio.exceptions.ConnectionError:
        print_error(f'Team server connection failed {args.team_server_uri}')
        return
    connect_client.team_server = client_websocket
    connect_client.cmdloop()


if __name__ == '__main__':
    exit(main())
