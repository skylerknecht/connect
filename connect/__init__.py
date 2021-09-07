from connect import cli, color, engine, util

util.__version__ = '0.9'

def run(ip, port, verbose):
    util.verbose = verbose
    connect_cli = cli.CommandLine('connect~#')
    connect_engine = engine.Engine(ip, port, connect_cli)
    color.normal(util.banner)
    connect_engine.run()
    return
