import json

from connect.output import Agent
from connect.team_server.models import AgentModel, db, ImplantModel, TaskModel

from flask_socketio import emit, disconnect

class TeamServerEvents:

    def __init__(self, key, sio_server):
        self.sio_server = sio_server
        self.key = key

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
            new_implant = ImplantModel()
            db.session.add(new_implant)
            db.session.commit()
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
                    db.session.commit()
                    emit('success', f'{num_deleted} implants deleted successfully')
                else:
                    implant = ImplantModel.query.filter_by(id=implant_id).first()
                    if implant:
                        db.session.delete(implant)
                        db.session.commit()
                        emit('success', 'Implant deleted successfully')
                    else:
                        emit('information', 'Implant not found')
            else:
                emit('error', 'No implant ID provided for delete')
        else:
            emit('error', 'Invalid action provided')

    def tasks(self):
        """
        Emit all available agents.
        """
        agents = [agent.get_agent() for agent in AgentModel.query.all()]
        self.sio_server.emit('agents', {'agents': agents})