import datetime

from connect import output
from connect.team_server.models import AgentModel, ImplantModel, TaskModel
from flask import jsonify, request, redirect

class TeamServerRoutes:

    def __init__(self, db, sio_server, task_manager):
        self.db = db
        self.sio_server = sio_server
        self.task_manager = task_manager

    def check_in_route(self, route):
        """
        The check_in route for agents to retrieve tasks and implants to authenticate.
        
        Parameters
        ----------
            route:    The requested route. 
        """
        if not request.get_data():
            output.display('DEBUG', f'Request made to /{route} with no data.')
            return redirect("https://www.google.com")

        try:
            batch_response = request.get_json(force=True)
        except:
            data = request.get_data().decode('utf-8')
            output.display('DEBUG', f'Failed to parse batch response:\n{data}')
            output.display('DEBUG', f'------------------------------')
            return redirect("https://www.google.com")

        batch_request = self.task_manager.process_tasks(batch_response)
        return jsonify(batch_request)