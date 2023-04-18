from . import socks

socks5server = socks.Proxy()
socks5server.run('127.0.0.1', 9050)