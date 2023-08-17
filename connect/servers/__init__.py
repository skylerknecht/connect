import logging
from .servers import TeamServer, HTTPListener

#os.environ['WERKZEUG_RUN_MAIN'] = 'true' -> This was actually a bug in older versions and can't be used anymore
log = logging.getLogger('werkzeug')
log.disabled = True

team_server = TeamServer()
http_listener = HTTPListener()
