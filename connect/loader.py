import os
import re

def download(data, filename):
    with open(f'{os.getcwd()}/connect/downloads/{filename}', 'wb') as fd:
        fd.write(data)

def retrieve_file(path):
    with open(path, 'rb') as fd:
        file_data = fd.read()
    return file_data
