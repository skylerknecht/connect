import argparse
import sys

from . import events
from . import models
from . import routes
from . import server
from connect import generate
from connect import output
from flask_socketio import SocketIO

sio_server = SocketIO(max_http_buffer_size=1e10)
key = generate.string_identifier(20)

team_server = server.TeamServer('Team Server', models.db, sio_server)
team_server_events = events.TeamServerEvents(key, models.db, sio_server)
team_server_routes = routes.TeamServerRoutes(models.db, sio_server)
team_server.create_database()
team_server.add_route('/<path:route>', 'check_in', team_server_routes.check_in_route, methods=['GET', 'POST'])    
team_server.add_event('agents', team_server_events.agents)
team_server.add_event('connect', team_server_events.connect)
team_server.add_event('implants', team_server_events.implants)
team_server.add_event('task', team_server_events.task)

def main():
    """
    The connect server controller.
    """
    parser = argparse.ArgumentParser('ConnectServer', 'Connect Server', conflict_handler='resolve')
    parser.add_argument('ip', metavar='ip', help='Server ip.')
    parser.add_argument('port', metavar='port', help='Server port.')
    parser.add_argument('--ssl', nargs=2, metavar=('CERT', 'KEY'), help='Use SSL.')
    args = parser.parse_args()
   
    if args.ssl:
        output.display('SUCCESS', f'Generated client args: https://{args.ip}:{args.port}/ {key}')
        team_server.run(args.ip, args.port, certfile=args.ssl[0], keyfile=args.ssl[1])
        return
    output.display('SUCCESS', f'Generated client args: http://{args.ip}:{args.port}/ {key}')
    team_server.run(args.ip, args.port, certfile=args.ssl[0], keyfile=args.ssl[1])


if __name__ == '__main__':
    sys.exit(main())
