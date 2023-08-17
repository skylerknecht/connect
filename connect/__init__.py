from connect.clients import cli
from connect.servers import team_server, http_listener
from connect.pyplant import pyplant
from connect.constants import BANNER

__version__ = '0.0.1'

pyplant = pyplant.Pyplant()

SUPPORTED_TOOLS = {
    cli.NAME: cli,
    http_listener.NAME: http_listener,
    pyplant.NAME: pyplant,
    team_server.NAME: team_server,
}
