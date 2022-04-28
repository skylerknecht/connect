import logging
import random
import os
import configparser

from connect.server.config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_json import FlaskJSON


def generate_id():
    new_id = [str(random.randint(1, 9)) for _ in range(0, 10)]
    new_id = ''.join(new_id)
    return new_id


config = configparser.ConfigParser()
config.read(f'{os.getcwd()}/.config')
downloads_directory = config['OPTIONAL']['downloads_directory']
if not downloads_directory:
    downloads_directory = f'{os.getcwd()}/connect/downloads/'

app = Flask(__name__, template_folder='../routes')
socket = SocketIO(app)
os.environ['WERKZEUG_RUN_MAIN'] = 'true'
log = logging.getLogger('werkzeug')
log.disabled = True
app.config.from_object(Config)
json = FlaskJSON(app)
db = SQLAlchemy(app)
from connect.server import database

db.create_all()
api_key = generate_id()

"""
Setup routes
"""

config = configparser.ConfigParser()
routes_path = f'{os.getcwd()}/connect/routes'
for route in os.listdir(routes_path):
    if not os.path.isdir(f'{routes_path}/{route}'):
        continue
    config.read(f'{routes_path}/{route}/config.ini')
    route_name = config['REQUIRED']['route_name']
    if database.Routes.query.filter_by(name=route_name).first():
        continue
    route = database.Routes(name=route_name, type=config['REQUIRED']['type'], description=config['REQUIRED']['description'])
    db.session.add(route)
    db.session.commit()


def run(args):
    from connect.server import routes
    from connect.routes import routes
    print(f'Client Arguments: http://{args.ip}:{args.port} {api_key} ')
    socket.run(app, host=args.ip, port=args.port)
