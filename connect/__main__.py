import argparse
import json
import sys
import threading

import connect.listeners.http.server as HTTPListener
import connect.listeners.http.endpoint as HTTPListenerEndpoints
import connect.team_server.server as TeamServer
import connect.team_server.endpoint as TeamServerEndpoints

from connect.models import db
from connect.output import print_info
from connect.configs.server import TeamServerConfig

http_listener = HTTPListener.HTTPListener('HTTP Listener', TeamServerConfig, db, HTTPListenerEndpoints.websocket)
http_listener.add_blueprint(HTTPListenerEndpoints.http_listener)

team_server = TeamServer.TeamServer('Team Server', TeamServerConfig, db, TeamServerEndpoints.login_manager, TeamServerEndpoints.websocket)
team_server.create_database()
team_server.add_blueprint(TeamServerEndpoints.team_server)
team_server.add_event('agents', TeamServerEndpoints.agents)
team_server.add_event('implants', TeamServerEndpoints.implants)
team_server.add_event('tasks', TeamServerEndpoints.tasks)


available_listeners = {
    'HTTP Listener': http_listener
}

def listeners(data):
    if not data:
        TeamServerEndpoints.websocket.emit('listeners', available_listeners.keys())
    data = json.loads(data)
    listener_name = data['listener_name'] if 'listener_name' in data.keys() else None
    if listener_name:
        listener_ip = data['ip']
        listener_port = data['port']
        print_info(f'Starting HTTP Listener: http://{listener_ip}:{listener_port}/')
        listener_thread = threading.Thread(target=available_listeners[listener_name].run, args=(listener_ip, listener_port))
        listener_thread.daemon = True
        listener_thread.start()

team_server.add_event('listeners', listeners)


def main():
    """
    The connect team server controller.
    """
    parser = argparse.ArgumentParser('TeamServer', 'Team Server', conflict_handler='resolve')
    parser.add_argument('ip', metavar='ip', help='Server ip.')
    parser.add_argument('port', metavar='port', help='Server port.')
    parser.add_argument('-d', '--debug', action='store_true', help='Debugging mode.')
    args = parser.parse_args()

    HTTPListenerEndpoints.debug_mode = args.debug if args.debug else False
    print_info(f'Generated Secret Key: {TeamServerEndpoints.key}')
    print_info(f'Starting Team Server: http://{args.ip}:{args.port}/')
    http_listener.team_server_uri = f'http://{args.ip}:{args.port}/'
    http_listener.team_server_key = TeamServerEndpoints.key
    team_server.run(args.ip, args.port)


if __name__ == '__main__':
    sys.exit(main())