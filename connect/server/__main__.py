import argparse
import sys

from . import endpoint
from . import server
from . import models
from . import stagers

from connect.configs.server import TeamServerConfig
from connect.output import print_success


team_server = server.TeamServer('Team Server', TeamServerConfig, models.db, endpoint.websocket)
team_server.create_database()
team_server.drop_stagers()
team_server.add_blueprint(endpoint.check_in)
team_server.add_event('connect', endpoint.connect)
team_server.add_event('agents', endpoint.agents)
team_server.add_event('stagers', endpoint.stagers)
team_server.add_event('new_job', endpoint.new_job)
team_server.add_event('implants', endpoint.implants)

for blueprint, stager in stagers.STAGERS.items():
    _stager = models.StagerModel(name=stager.name, endpoint=stager.endpoint, delivery=stager.delivery)
    team_server.add_stager(_stager)
    team_server.add_blueprint(blueprint)


def main():
    """
    The connect server controller.
    """
    parser = argparse.ArgumentParser('ConnectServer', 'Connect Server', conflict_handler='resolve')
    parser.add_argument('ip', metavar='ip', help='Server ip.')
    parser.add_argument('port', metavar='port', help='Server port.')
    args = parser.parse_args()

    print_success(f'Generated client args: http://{args.ip}:{args.port}/ {endpoint.key}')
    team_server.run(args.ip, args.port)


if __name__ == '__main__':
    sys.exit(main())
