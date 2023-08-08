from flask import Blueprint

check_in_blueprint = Blueprint('check_in', __name__)


@check_in_blueprint.route('/')
def check_in():
    return 'lol'