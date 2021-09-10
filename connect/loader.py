import os
import re

from connect import util
from collections import namedtuple

END = re.compile(r'\/\/end')
START = re.compile(r'\/\/start\.[\w\s]+\.[\w\s]+')

def discover_functions(file_regex):
    _file_regex = re.compile(file_regex)
    _files = [file for file in os.listdir(f'{os.getcwd()}/connect/templates/extensions/') if _file_regex.match(file)]
    functions = {}
    function_name = ''
    function_description = ''
    function_definiton = ''
    for file in _files:
        with open(f'{os.getcwd()}/connect/templates/extensions/{file}', 'r') as library:
            for line in library:
                if not line:
                    continue
                if START.match(line):
                    properties = line.split('.')
                    function_name = properties[1]
                    function_description = properties[2]
                    option_type = properties[3]
                    continue
                if END.match(line):
                    functions[function_name] = util.Function(function_name, function_description, function_definiton, option_type)
                    function_name = ''
                    function_description = ''
                    function_definiton = ''
                    option_type = ''
                    continue
                if function_name:
                    function_definiton = function_definiton + line.rstrip()
    return functions

def download(data, filename):
    with open(f'{os.getcwd()}/connect/downloads/{filename}', 'wb') as fd:
        fd.write(data)
