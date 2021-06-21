from . import cli, engine
import threading
import time

__version__ = '0.3'

def run(ip, port):
    connect_engine = threading.Thread(target=engine.run,args=(ip, port))
    connect_engine.daemon = True
    connect_engine.start()
    cli.display_banner()
    color.warning('Server Information:')
    time.sleep(.1)
    cli.run()
    return
