import configparser
import os
from connect.client import cli

config = configparser.ConfigParser()
config.read(f'{os.getcwd()}/.config')
downloads_directory = config['OPTIONAL']['downloads_directory']
if not downloads_directory:
    downloads_directory = f'{os.getcwd()}/connect/downloads/'

server_uri = None
api_key = None
connections = {}
current_connection = ''


def run():
    client = cli.Client()
    client.cmdloop()