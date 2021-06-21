from . import cli, engine
import threading
import time

__version__ = '0.3'

def run(ip, port):
    engine.host = ip
    engine.port = int(port)
    connect_engine = threading.Thread(target=engine.run)
    connect_engine.daemon = True
    connect_engine.start()
    cli.display_banner()
    color.information('Server Information:')
    time.sleep(.1)
    cli.run()
    return
