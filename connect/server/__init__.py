import logging
import random
import os
import configparser
import importlib.util

from connect.server.config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_json import FlaskJSON


app = Flask(__name__, template_folder='stagers')
os.environ['WERKZEUG_RUN_MAIN'] = 'true'
log = logging.getLogger('werkzeug')
log.disabled = True
app.config.from_object(Config)
json = FlaskJSON(app)
db = SQLAlchemy(app)
from connect.server import database

db.create_all()
api_key = [str(random.randint(1, 9)) for _ in range(0, 10)]
api_key = ''.join(api_key)


"""
If there are no routes then configure them in the database.
"""
if not database.Routes.query.filter_by(name='check_in').first():
    check_in = database.Routes(name='check_in')
    db.session.add(check_in)
    db.session.commit()

config = configparser.ConfigParser()
stagers_path = f'{os.getcwd()}/connect/server/stagers'
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
    from connect.server.stagers import routes
    print(f'Client Arguments: http://{args.ip}:{args.port} {api_key} ')
    app.run(host=args.ip, port=args.port)
