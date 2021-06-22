import threading
import time

from connect import util, color, cli

util.__version__ = '0.3'

def setup_cli():
    connect_cli = cli.CommandLine('connect~#')
    connect_cli.display_banner()
    color.information('Server Information:')
    time.sleep(.1)
    connect_cli.run()

def setup_engine(ip, port):
    engine.host = ip
    engine.port = int(port)
    connect_engine = threading.Thread(target=engine.run)
    connect_engine.daemon = True
    connect_engine.start()

def run(ip, port):
    setup_engine(ip, port)
    setup_cli()
    return
