import os
import logging


os.environ['WERKZEUG_RUN_MAIN'] = 'true'
log = logging.getLogger('werkzeug')
log.disabled = True


class TeamServerConfig:
    """
    App Config for the team listener.
    """
    TEMPLATES_AUTO_RELOAD = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = '463f1eabe8f830653b2ffd8a89cd1272'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///.backup/connect.db'
    JSON_SORT_KEYS = False
