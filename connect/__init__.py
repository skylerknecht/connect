from connect import cli, engine, util

cli.CommandLine.__version__ = '1.5'

def run(args):
    util.ssl = args.ssl
    connect_cli = cli.CommandLine('connect~#', messages={'disconnected': cli.CommandLine.Message(cli.CommandLine.COLORS['red'], ''),
                                                         'connected': cli.CommandLine.Message(cli.CommandLine.COLORS['green'], ''),
                                                         'stale': cli.CommandLine.Message(cli.CommandLine.COLORS['yellow'], '')
                                                        })
    connect_engine = engine.Engine(args.IP, args.PORT, connect_cli)
    connect_cli.print('default', util.banner)
    connect_engine.run()
    return
