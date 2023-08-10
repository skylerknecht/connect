import os

from connect import generate

TEMPLATES_AUTO_RELOAD = True
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = 'sqlite:///connect.db'
JSON_SORT_KEYS = False
SECRET_KEY = os.environ.get('SECRET_KEY')
