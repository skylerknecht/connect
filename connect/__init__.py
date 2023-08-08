import logging
from connect.server import server

__version__ = '0.0.1'

http_listener = server.HTTPListener()
socketio_listener = server.SocketIOListener()
team_server = server.TeamServer()

log = logging.getLogger('werkzeug')
log.disabled = True

SUPPORTED_CONTROLLERS = {
    http_listener.NAME: http_listener,
    socketio_listener.NAME: socketio_listener,
    team_server.NAME: team_server,
}
