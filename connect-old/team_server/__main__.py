import argparse
import sys

from . import events
from . import models
from . import routes
from . import server
from . import task_manager
from connect import generate
from connect import output
from connect import socks
from flask_socketio import SocketIO

sio_server = SocketIO(max_http_buffer_size=1e10, ping_timeout=60) 
key = generate.string_identifier(20)

parser = argparse.ArgumentParser('ConnectServer', 'Connect Server', conflict_handler='resolve')
parser.add_argument('ip', metavar='ip', help='Server ip.')
parser.add_argument('port', metavar='port', help='Server port.')
parser.add_argument('--ssl', nargs=2, metavar=('CERT', 'KEY'), help='Use SSL.')
parser.add_argument('--debug', action='store_true', help='Enable debug mode.')
args = parser.parse_args()

output.debug = args.debug

team_server_uri = f'https://{args.ip}:{args.port}/' if args.ssl else f'http://{args.ip}:{args.port}/'
team_server = server.TeamServer('Team Server', models.db, sio_server)
team_server_task_manager = task_manager.TaskManager(models.db, sio_server)
team_server_socks_proxy_manager = socks.socks.ProxyManager(team_server_uri, key)
team_server_events = events.TeamServerEvents(models.db, sio_server, key, team_server_socks_proxy_manager)
team_server_routes = routes.TeamServerRoutes(models.db, sio_server, team_server_task_manager)
team_server.create_database()
team_server.add_route('/<path:route>', 'check_in', team_server_routes.check_in_route, methods=['GET', 'POST'])    
team_server.add_event('agents', team_server_events.agents)
team_server.add_event('connect', team_server_events.connect)
team_server.add_event('implants', team_server_events.implants)
team_server.add_event('socks', team_server_events.socks)
team_server.add_event('task', team_server_events.task)
team_server.add_event('version', team_server_events.version)

if args.ssl:
    output.display('SUCCESS', f'Generated client args: https://{args.ip}:{args.port}/ {key}')
    team_server.run(args.ip, args.port, certfile=args.ssl[0], keyfile=args.ssl[1])
    sys.exit()

output.display('SUCCESS', f'Generated client args: http://{args.ip}:{args.port}/ {key}')
team_server.run(args.ip, args.port)