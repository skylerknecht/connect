import json

from connect.output import Task
from connect.team_server.models import AgentModel, ImplantModel, TaskModel

from flask_socketio import emit, disconnect

class TeamServerEvents:

    def __init__(self, key, db, sio_server):
        self.sio_server = sio_server
        self.key = key
        self.db = db

    def commit(self, models: list):
        """
        Commits model object changes to the database.
        :param models: A list of models.
        """
        for model in models:
            self.db.session.add(model)
        self.db.session.commit() 

    def connect(self, auth):
        """
        This event is triggered on client connection requests.
        If the authentication data does not match the generated key,
        then a disconnect event is triggered.
        :param auth:
        """
        if not auth == self.key:
            disconnect()

    def agents(self):
        """
        Emit all available agents.
        """
        agents = [agent.get_agent() for agent in AgentModel.query.all()]
        self.sio_server.emit('agents', {'agents': agents})

    def implants(self, data):
        """
        Emit all available implants.
        """
        if not data:
            implants = [implant.get_implant() for implant in ImplantModel.query.all()]
            self.sio_server.emit('implants', {'implants': implants})
            return
        
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            emit('error', 'Invalid JSON provided')
            return

        action = data.get('action')
        if action == 'create':
            new_implant = ImplantModel(options=data.get('options'))
            self.db.session.add(new_implant)
            self.db.session.commit()
            new_implant_dict = {
                'id': new_implant.id,
                'key': new_implant.key
            }
            emit('success', f'Implant created successfully {new_implant_dict}')
        elif action == 'delete':
            implant_id = data.get('implant_id')
            if implant_id:
                if implant_id == 'all':
                    num_deleted = ImplantModel.query.delete()
                    self.db.session.commit()
                    emit('success', f'{num_deleted} implants deleted successfully')
                else:
                    implant = ImplantModel.query.filter_by(id=implant_id).first()
                    if implant:
                        self.db.session.delete(implant)
                        self.db.session.commit()
                        emit('success', 'Implant deleted successfully')
                    else:
                        emit('information', 'Implant not found')
            else:
                emit('error', 'No implant ID provided for delete')
        else:
            emit('error', 'Invalid action provided')

    def task(self, data):
        """
        This event schedules a new task to be sent to the agent.
        The *data* excpeted is {'name':'', 'agent_name':'', 'parameters':'', type:''}
        :param data:
        """
        print(data)
        data = json.loads(data)
        task = Task(*data['task'])
        agent = AgentModel.query.filter_by(name=data['agent']).first()
        task = TaskModel(name=task.name, description=task.description, parameters=task.parameters, type=task.type,  agent=agent)
        self.commit([task])