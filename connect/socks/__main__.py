from . import socks

socks5server = socks.Proxy('192.168.1.15', 9050)
socks5server.run()