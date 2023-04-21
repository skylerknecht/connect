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
        implant = ImplantModel.query.filter_by(key=route).first()

        if implant:
            agent = self.check_in_implant(implant)
            if not agent:
                return '[]'
            check_in_task = self.create_check_in_task(agent)
            initial_batch_request = [{
                "connectrpc": "2.0",
                "id": str(check_in_task.id),
                "name": check_in_task.name,
                "parameters": check_in_task.parameters
            }]
            self.sio_server.emit('information', f'Sending initial check in reuqest to {agent.name}')
            return(jsonify(initial_batch_request))
        
        if not request.get_data():
            output.display('ERROR', f'Request made to /{route} with no data.')
            return redirect("https://www.google.com")

        try:
            batch_response = request.get_json(force=True)
        except:
            data = request.get_data().decode('utf-8')
            output.display('DEFAULT', f'Failed to parse batch response:\n{data}')
            output.display('DEFAULT', f'------------------------------')
            return redirect("https://www.google.com")

        batch_request = self.task_manager.process_tasks(batch_response)
        return jsonify(batch_request)

    def commit(self, models: list):
        """
        Commits model object changes to the database.
        :param models: A list of models.
        """
        for model in models:
            self.db.session.add(model)
        self.db.session.commit()

    def check_in_implant(self, implant):
        self.sio_server.emit('information', f'Implant {implant.id} checked in creating Agent')
        try:
            agent = AgentModel(implant=implant)
            self.commit([agent])
        except Exception as e:
            self.sio_server.emit('error', f'Failed to create agent:\n {e}')
            return None
        self.sio_server.emit('information', f'Created agent {agent.name}')
        return agent
    
    def create_check_in_task(self, agent):
        check_in_task = TaskModel(name='check_in', description='check in', agent=agent, type=0)
        check_in_task.completed = datetime.datetime.now()
        check_in_task.sent = datetime.datetime.now()
        self.commit([check_in_task])
        return check_in_task