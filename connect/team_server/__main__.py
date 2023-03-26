from . import events
from . import models
from . import routes
from . import server
from connect import generate
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
print(key)
team_server.run('127.0.0.1', '8080')