import threading
import time

from connect import cli, color, server, util

util.__version__ = '0.3'

def setup_cli(engine):
    connect_cli = cli.CommandLine('connect~#')
    connect_cli.display_banner()
    color.information('Server Information:')
    time.sleep(.1)
    connect_cli.run()

def setup_engine(ip, port):
    connect_engine = engine.Engine(ip, port)
    util.engine = connect_engine
    connect_server = threading.Thread(target=server.run)
    connect_server.daemon = True
    connect_server.start()

def run(ip, port):
    setup_cli()
    return
