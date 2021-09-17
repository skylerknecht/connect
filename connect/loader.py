import os
import re

def download(data, filename):
    with open(f'{os.getcwd()}/connect/downloads/{filename}', 'wb') as fd:
        fd.write(data)
