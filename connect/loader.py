import os
import re

from connect import color

def download(data, filename):
    with open(f'{os.getcwd()}/connect/downloads/{filename}', 'wb') as fd:
        fd.write(data)

def retrieve_file(path):
    path = f'{os.getcwd()}{path}'
    if not os.path.exists(path):
        color.information(f'{path} does not exist.')
        return None
    with open(path, 'rb') as fd:
        file_data = fd.read(path)
    return file_data
