from connect import cli, color, engine, util

util.__version__ = '1.2'

def run(args):
    util.verbose = args.verbose
    util.ssl = args.ssl
    connect_cli = cli.CommandLine('connect~#')
    connect_engine = engine.Engine(args.IP, args.PORT, connect_cli)
    color.normal(util.banner)
    connect_engine.run()
    return
