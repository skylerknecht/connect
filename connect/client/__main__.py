import argparse
import json
import socketio
import sys

from . import client
from connect import output
from datetime import datetime

sio_client = socketio.Client()
options = client.Options(sio_client)
cli = client.Interface(options)

@sio_client.event
def agents(data):
    agents = data['agents']
    cli.notify('DEFAULT', '{:<40}{:<10}{:<40}'.format('', '[AGENTS]', ''))
    cli.notify('DEFAULT', '')
    cli.notify('DEFAULT', '{:<20}{:<10}{:<20}{:<20}{:<20}{:<20}'.format('Name', 'Delta', 'Username', 'Hostname', 'IP', 'OS'))
    cli.notify('DEFAULT', '{:<20}{:<10}{:<20}{:<20}{:<20}{:<20}'.format('-'*4, '-'*5, '-'*8, '-'*8, '-'*2, '-'*2))
    for index, agent in enumerate(agents):
        agents[index] = agent = output.deserialize_agent_json_object(agent)
        check_in = datetime.fromisoformat(agent.check_in)
        delta = int((datetime.now() - check_in).total_seconds())
        cli.notify('DEFAULT', '{:<20}{:<10}{:<20}{:<20}{:<20}{:<20}'.format(agent.name, delta, agent.username, agent.hostname, agent.ip, agent.os))
    options.Agents.extend(agents)


@sio_client.event
def error(data):
    cli.notify('ERROR', data)

@sio_client.event
def success(data):
    cli.notify('SUCCESS', data)

@sio_client.event
def implants(data):
    implants = data['implants']
    cli.notify('DEFAULT', '{:<5}{:<10}{:<5}'.format('', '[IMPLANTS]', ''))
    cli.notify('DEFAULT', '')
    cli.notify('DEFAULT', '{:<15}{:<15}'.format('ID', 'KEY'))
    cli.notify('DEFAULT', '{:<15}{:<15}'.format('-'*2, '-'*3))
    for index, implant in enumerate(implants):
        implants[index] = output.Implant(*implant)
        implant = implants[index]
        cli.notify('DEFAULT', '{:<15}{:<15}'.format(implant.id, implant.key))

@sio_client.event
def information(data):
    cli.notify('INFORMATION', data)

def main():
    """
    The connect client controller. This function accepts arguments to connect to the
    socketio teamserver and starts the command line interface.
    """
    parser = argparse.ArgumentParser('ConnectClient', 'python3 -m connect.client <ip:port> <key>', conflict_handler='resolve')
    parser.add_argument('team_server_uri', help='Team Server\'s URI.')
    parser.add_argument('key', help='Team Server\'s Key.')
    args = parser.parse_args()
    try:
        sio_client.connect(args.team_server_uri, auth=args.key)
    except socketio.exceptions.ConnectionError:
        output.display('ERROR', f'Connection could not be stablished to {args.team_server_uri}')
        return
    cli.run()

if __name__ == '__main__':
    sys.exit(main())