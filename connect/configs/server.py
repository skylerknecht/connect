import os
import logging

HEADERS = {}

ENDPOINTS = []
with open(f'{os.getcwd()}/resources/endpoints.txt') as endpoints:
    for endpoint in endpoints:
        ENDPOINTS.append(endpoint)

os.environ['WERKZEUG_RUN_MAIN'] = 'true'
log = logging.getLogger('werkzeug')
log.disabled = True


class HttpListenerConfig:
    """
    App Config for the http listeners.
    """
    TEMPLATES_AUTO_RELOAD = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = '463f1eabe8f830653b2ffd8a89cd1272'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///connect.db'
    JSON_SORT_KEYS = False


class TeamListenerConfig:
    """
    App Config for the team listener.
    """
    TEMPLATES_AUTO_RELOAD = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = '463f1eabe8f830653b2ffd8a89cd1272'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///connect.db'
    JSON_SORT_KEYS = False
