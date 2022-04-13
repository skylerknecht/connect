import logging
import random
import os

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
if not database.Routes.query.first():
    check_in = database.Routes(name='check_in')
    jscript = database.Routes(name='jscript')
    db.session.add(check_in)
    db.session.add(jscript)
    db.session.commit()


def run(args):
    from connect.server import routes
    print(f'Client Arguments: http://{args.ip}:{args.port} {api_key} ')
    app.run(host=args.ip, port=args.port)
