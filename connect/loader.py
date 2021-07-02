import os
import re

from connect import color, util
from collections import namedtuple

Function = namedtuple('Function', ['name', 'description', 'definiton', 'format'])
END = re.compile(r'\/\/end')
START = re.compile(r'\/\/start\.[\w\s]+\.[\w\s]+')

def discover_functions(file_regex):
    _file_regex = re.compile(file_regex)
    _files = [file for file in os.listdir(f'{os.getcwd()}/connect/templates/extensions/') if _file_regex.match(file)]
    functions = []
    function_name = ''
    function_description = ''
    function_definiton = ''
    for file in _files:
        file_type = file.split('.')[1]
        with open(f'{os.getcwd()}/connect/templates/extensions/{file}', 'r') as library:
            for line in library:
                if not line:
                    continue
                if START.match(line):
                    properties = line.split('.')
                    function_name = properties[1]
                    function_description = properties[2]
                    continue
                if END.match(line):
                    functions.append(Function(function_name, function_description, function_definiton, file.split('.')[1]))
                    function_name = ''
                    function_description = ''
                    function_definiton = ''
                    continue
                if function_name:
                    function_definiton = function_definiton + line.rstrip()
    util.functions.extend(functions)
