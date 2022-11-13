import datetime
import json

from connect.generate import digit_identifier, name_identifier
from connect.generate import generate_sleep, generate_jitter, generate_endpoints
from connect.output import Agent, Stager, Implant
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class StagerModel(db.Model):
    type = db.Column(db.String, primary_key=True)
    endpoints = db.Column(db.Integer, nullable=True)

    def get_stager(self):
        return Stager(self.type, self.endpoints)


class ImplantModel(db.Model):
    # properties
    key = db.Column(db.String, primary_key=True, default=digit_identifier)
    sleep = db.Column(db.String, default=generate_sleep)
    jitter = db.Column(db.String, default=generate_jitter)
    endpoints = db.Column(db.String, default=generate_endpoints)
    _commands = db.Column(db.String)
    _available_commands = db.Column(db.String, default='{}')

    # relationships
    agents = db.relationship('AgentModel', backref='implant', lazy=True)

    @property
    def commands(self):
        if not self._commands:
            return ''
        return [command for command in self._commands.split(',')]

    @commands.setter
    def commands(self, value):
        self._commands = value
    
    @property
    def available_commands(self):
        return json.loads(self._available_commands)

    @available_commands.setter
    def available_commands(self, value):
        self._available_commands = json.dumps(value)

    def get_implant(self):
        return Implant(self.key)


class AgentModel(db.Model):
    # properties
    name = db.Column(db.String, primary_key=True, default=name_identifier)
    check_in = db.Column(db.DateTime, default=datetime.datetime.fromtimestamp(823879740.0))
    _loaded_commands = db.Column(db.String)
    sleep = db.Column(db.String)
    jitter = db.Column(db.String)

    # system information
    username = db.Column(db.String, nullable=False, default='....')
    hostname = db.Column(db.String, nullable=False, default='....')
    os = db.Column(db.String, nullable=False, default='....')
    integrity = db.Column(db.String, nullable=False, default='....')
    pid = db.Column(db.String, nullable=False, default='....')

    # relationships
    implant_key = db.Column(db.String, db.ForeignKey(ImplantModel.key))
    parent_name = db.Column(db.String, db.ForeignKey(name))
    children = db.relationship('AgentModel', backref=db.backref('parent', remote_side=[name]), lazy=True)
    tasks = db.relationship('TaskModel', backref='agent', lazy=True, order_by='TaskModel.created')

    @property
    def loaded_commands(self):
        if not self._loaded_commands:
            return ''
        return [str(command) for command in self._loaded_commands.split(',')]

    @loaded_commands.setter
    def loaded_commands(self, value):
        self._loaded_commands = value

    def get_agent(self):
        return Agent(self.name, str(self.check_in), self.username, self.hostname, self.pid, self.integrity,
                     self.implant.commands, self.sleep, self.jitter)


class TaskModel(db.Model):
    identifier = db.Column(db.Integer, primary_key=True, default=digit_identifier)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    _arguments = db.Column(db.String, nullable=False, default='')
    agent_name = db.Column(db.Integer, db.ForeignKey(AgentModel.name), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    completed = db.Column(db.DateTime)
    sent = db.Column(db.DateTime)
    type = db.Column(db.Integer, nullable=False)
    results = db.Column(db.Text, default='No results.')

    @property
    def arguments(self):
        return [str(x) for x in self._arguments.split(',')]

    @arguments.setter
    def arguments(self, value):
        self._arguments = value


