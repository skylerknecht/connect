import datetime
import json

from connect.output import Agent, Implant, Task
from connect.generate import digit_identifier, name_identifier, string_identifier
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ImplantModel(db.Model):
    # properties
    id = db.Column(db.String, primary_key=True, default=digit_identifier)
    name = db.Column(db.String, unique=True, nullable=False)
    key = db.Column(db.String, unique=True, default=string_identifier)
    location = db.Column(db.String, nullable=False)
    _options = db.Column(db.String, nullable=False)

    # relationships
    agents = db.relationship('AgentModel', backref='implant', lazy=True)

    @property
    def options(self):
        if not self._options:
            return '' 
        return json.loads(self._options)

    @options.setter
    def options(self, value):
        self._options = json.dumps(value)


    def get_implant(self):
        return Implant(self.name, self.id, self.key, self.location)
    
class AgentModel(db.Model):
    # properties
    # ToDo: Change this to ID instead of Name.
    name = db.Column(db.String, primary_key=True, default=digit_identifier)
    check_in = db.Column(db.DateTime, default=datetime.datetime.fromtimestamp(823879740.0))
    _loaded_modules = db.Column(db.String, nullable=False, default='')

    # relationships
    implant_key = db.Column(db.String, db.ForeignKey(ImplantModel.key))
    tasks = db.relationship('TaskModel', backref='agent', order_by='TaskModel.created')

    # system information
    username = db.Column(db.String, nullable=False, default='....')
    hostname = db.Column(db.String, nullable=False, default='....')
    os = db.Column(db.String, nullable=False, default='....')
    ip = db.Column(db.String, nullable=False, default='....')
    integrity = db.Column(db.String, nullable=False, default='....')
    pid = db.Column(db.String, nullable=False, default='....')

    @property
    def loaded_modules(self):
        if not self._loaded_modules:
            return []
        return [str(x) for x in self._loaded_modules.split(',')]

    @loaded_modules.setter
    def loaded_modules(self, value):
        self._loaded_modules = value

    def get_agent(self):
        return Agent(self.name, str(self.check_in), self.username, self.hostname, self.ip, self.os, self.implant.options, self.implant.name)


class TaskModel(db.Model):
    # properties
    id = db.Column(db.Integer, primary_key=True, default=digit_identifier)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    _parameters = db.Column(db.String, nullable=False, default='')
    created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    completed = db.Column(db.DateTime)
    sent = db.Column(db.DateTime)
    type = db.Column(db.Integer, nullable=False)
    results = db.Column(db.Text, default='No results.')

    # relationships
    agent_name = db.Column(db.Integer, db.ForeignKey(AgentModel.name))

    @property
    def parameters(self):
        if not self._parameters:
            return []
        return [str(x) for x in self._parameters.split(',')]

    @parameters.setter
    def parameters(self, value):
        self._parameters = value

    def get_task(self):
        return Task(self.name, self.description, self.parameters, self.type)