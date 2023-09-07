import os

TEMPLATES_AUTO_RELOAD = True
JSON_SORT_KEYS = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = 'sqlite:///connect.db'
SECRET_KEY = open(f'{os.getcwd()}/instance/.key', 'r').read()
