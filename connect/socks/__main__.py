from . import local_socks

socks5server = local_socks.Proxy()
socks5server.run('192.168.1.15', 9050)