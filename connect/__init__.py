from connect import cli, engine

__version__ = '0.1'

def run(ip, port):
    connect_server = engine.Server(ip, port)
    return cli.run(connect_server)
