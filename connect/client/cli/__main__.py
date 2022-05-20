import argparse
import socketio
import json

from . import client
from . import command_sets
from connect.convert import base64_to_string
from connect.output import print_agents_table, print_stagers_table
from connect.output import print_success, print_status
from connect.output import Agent, Stager
from os import getcwd
from sys import exit
from time import sleep

client_websocket = socketio.Client()
connect_client = client.ConnectClient(allow_cli_args=False, shortcuts={'*': 'interact', '!': 'shell', '?': 'help -v'},
                                      persistent_history_file=f'{getcwd()}/.history')


def post_job(job):
    job_json = f'{{"agent_name":"{connect_client.current_agent}",{job}}}'
    client_websocket.emit('new_job', job_json)


for command_set in command_sets.COMMAND_SETS:
    connect_client.register_command_set(command_set(post_job))

connect_client.disable_command_sets()


@client_websocket.event
def connected(data):
    print('\n')
    print_success(data)


@client_websocket.event
def job_sent(data):
    print('\n')
    print_status(data)


@client_websocket.event
def job_results(data):
    data = json.loads(data)
    print('\n')
    print_status(data['banner'])
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


def main():
    """
    The connect client controller.
    """

    parser = argparse.ArgumentParser('ConnectClient', 'Connect Client', conflict_handler='resolve')
    parser.add_argument('team_server_uri', help='Team Server\'s URI.')
    parser.add_argument('key', help='Team Server\'s Key.')
    args = parser.parse_args()

    client_websocket.connect(args.team_server_uri, auth=args.key)
    connect_client.team_listener = client_websocket
    connect_client.cmdloop()


if __name__ == '__main__':
    exit(main())
