from connect.client import cli
#import connect.stagers.commands

server_uri = None
api_key = None
connections = {}
current_connection = ''


def run():
    client = cli.Client()
    client.cmdloop()