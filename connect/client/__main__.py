import argparse
import json
import socketio
import sys
import urllib3

from . import client
from connect import output
from connect import convert
from datetime import datetime

sio_client = socketio.Client(ssl_verify=False, logger=False)
options = client.Options(sio_client)
cli = client.Interface(options)

@sio_client.event
def agent_connected(data):
    agent_name = data['agent'][0]
    cli.notify('SUCCESS', f'Agent {agent_name} is connected!')
    for agent in options.Agents:
        if agent.name == agent_name:            
            return
    agent = output.deserialize_agent_json_object(data['agent'])
    options.Agents.append(agent)

@sio_client.event
def agents(data):
    agents = data['agents']
    cli.notify('DEFAULT', '{:<55}{:<10}{:<45}'.format('', '[AGENTS]', ''))
    cli.notify('DEFAULT', '')
    cli.notify('DEFAULT', '{:<20}{:<20}{:<10}{:<30}{:<20}{:<20}{:<20}'.format('ID', 'Implant', 'Delta', 'Username', 'Hostname', 'IP', 'OS'))
    cli.notify('DEFAULT', '{:<20}{:<20}{:<10}{:<30}{:<20}{:<20}{:<20}'.format('-'*4, '-'*6, '-'*5, '-'*8, '-'*8, '-'*2, '-'*2))
    for index, agent in enumerate(agents):
        agents[index] = agent = output.deserialize_agent_json_object(agent)
        check_in = datetime.fromisoformat(agent.check_in)
        delta = int((datetime.now() - check_in).total_seconds())
        if delta < 60 or data['all'] == "True":
            cli.notify('DEFAULT', '{:<20}{:<20}{:<10}{:<30}{:<20}{:<20}{:<20}'.format(agent.name, agent.implant, delta, agent.username, agent.hostname, agent.ip, agent.os))
    options.Agents = agents


@sio_client.event
def error(data):
    cli.notify('ERROR', data)

@sio_client.event
def implants(data):
    implants = data['implants']
    cli.notify('DEFAULT', '{:<12}{:<10}{:<12}'.format('', '[IMPLANTS]', ''))
    cli.notify('DEFAULT', '')
    cli.notify('DEFAULT', '{:<15}{:<15}{:<15}'.format('NAME', 'ID', 'KEY'))
    cli.notify('DEFAULT', '{:<15}{:<15}{:<15}'.format('-'*4, '-'*2, '-'*3))
    for index, implant in enumerate(implants):
        implants[index] = output.Implant(*implant)
        implant = implants[index]
        cli.notify('DEFAULT', '{:<15}{:<15}{:<15}'.format(implant.name, implant.id, implant.key))
        

@sio_client.event
def error(data):
    cli.notify('ERROR', data)

@sio_client.event
def information(data):
    cli.notify('INFORMATION', data)

@sio_client.event
def success(data):
    cli.notify('SUCCESS', data)

@sio_client.event
def task_results(data):
    data = json.loads(data)
    cli.notify('SUCCESS', data['banner'])
    cli.notify('DEFAULT', convert.base64_to_string(data['results']))

@sio_client.event
def task_error(data):
    data = json.loads(data)
    cli.notify('ERROR', data['banner'])
    cli.notify('DEFAULT', convert.base64_to_string(data['results']))

def main():
    """
    The connect client controller. This function accepts arguments to connect to the
    socketio teamserver and starts the command line interface.
    """
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    parser = argparse.ArgumentParser('ConnectClient', 'python3 -m connect.client <team_server_uri> <key>', conflict_handler='resolve')
    parser.add_argument('team_server_uri', help='Team Server\'s URI.')
    parser.add_argument('key', help='Team Server\'s Key.')
    args = parser.parse_args()
    cli.run(args.team_server_uri, args.key)

if __name__ == '__main__':
    sys.exit(main())