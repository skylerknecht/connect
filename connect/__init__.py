import time

from connect import cli, color, util

util.__version__ = '0.3'

def run(ip, port, verbose):
    util.verbose = verbose
    loader.discover_functions(r'stdlib\.\w+')
    connect_cli = cli.CommandLine('connect~#')
    connect_engine = engine.Engine(ip, port, connect_cli)
    color.normal(util.banner)
    connect_engine.run()
    return
