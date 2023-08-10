import logging
from connect.clients import cli
from connect.servers import servers
from connect.pyplant import pyplant
from connect.constants import BANNER

__version__ = '0.0.1'

cli = cli.CLI()
http_listener = servers.HTTPListener()
pyplant = pyplant.Pyplant()
socketio_listener = servers.SocketIOListener()
team_server = servers.TeamServer()

log = logging.getLogger('werkzeug')
log.disabled = True

SUPPORTED_TOOLS = {
    cli.NAME: cli,
    http_listener.NAME: http_listener,
    pyplant.NAME: pyplant,
    socketio_listener.NAME: socketio_listener,
    team_server.NAME: team_server,
}
