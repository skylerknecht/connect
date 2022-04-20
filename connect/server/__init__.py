import logging
import random
import os
import configparser

from connect.server.config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
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

app = Flask(__name__, template_folder='../stagers')
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
If there are no routes then configure them in the database.
"""
if not database.Routes.query.filter_by(name='check_in').first():
    check_in = database.Routes(name='check_in')
    db.session.add(check_in)
    db.session.commit()

config = configparser.ConfigParser()
stagers_path = f'{os.getcwd()}/connect/stagers'
for stager in os.listdir(stagers_path):
    config.read(f'{stagers_path}/{stager}/config.ini')
    route_name = config['REQUIRED']['route_name']
    if database.Routes.query.filter_by(name=route_name).first():
        continue
    route = database.Routes(name=route_name, description=config['REQUIRED']['description'])
    db.session.add(route)
    db.session.commit()


def run(args):
    from connect.server import routes
    from connect.stagers import routes
    print(f'Client Arguments: http://{args.ip}:{args.port} {api_key} ')
    app.run(host=args.ip, port=args.port)
