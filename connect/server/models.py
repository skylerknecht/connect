import datetime
import json

from connect.generate import digit_identifier, name_identifier
from connect.generate import generate_sleep, generate_jitter, generate_endpoints
from connect.output import Agent, Stager, Implant
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class StagerModel(db.Model):
    type = db.Column(db.String, primary_key=True)
    _endpoints = db.Column(db.Integer, nullable=True)

    @property
    def endpoints(self):
        return json.loads(self._endpoints)

    @endpoints.setter
    def endpoints(self, value):
        self._endpoints = json.dumps(value)


    def get_stager(self):
        return Stager(self.type, self.endpoints)


class ImplantModel(db.Model):
    # properties
    key = db.Column(db.String, primary_key=True, default=digit_identifier)
    sleep = db.Column(db.String, default=generate_sleep)
    jitter = db.Column(db.String, default=generate_jitter)
    endpoints = db.Column(db.String, default=generate_endpoints)
    _startup_commands = db.Column(db.String)
    _commands = db.Column(db.String)
    _available_modules = db.Column(db.String, default='{}')
    
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
    def available_modules(self):
        return json.loads(self._available_modules)

    @available_modules.setter
    def available_modules(self, value):
        self._available_modules = json.dumps(value)

    @property
    def startup_commands(self):
        if not self._startup_commands:
            return ''
        return [command for command in self._startup_commands.split(',')]

    @startup_commands.setter
    def startup_commands(self, value):
        self._startup_commands = value

    def get_implant(self):
        return Implant(self.key)


class AgentModel(db.Model):
    # properties
    name = db.Column(db.String, primary_key=True, default=name_identifier)
    check_in = db.Column(db.DateTime, default=datetime.datetime.fromtimestamp(823879740.0))
    _loaded_modules = db.Column(db.String)
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
    tasks = db.relationship('TaskModel', backref='agent', order_by='TaskModel.created')

    @property
    def loaded_modules(self):
        if not self._loaded_modules:
            return ''
        return [module for module in self._loaded_modules.split(',')]

    @loaded_modules.setter
    def loaded_modules(self, value):
        self._loaded_modules = value

    def get_agent(self):
        return Agent(self.name, str(self.check_in), self.username, self.hostname, self.pid, self.integrity,
                     self.implant.commands, self.sleep, self.jitter)


class TaskModel(db.Model):
    identifier = db.Column(db.Integer, primary_key=True, default=digit_identifier)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    _arguments = db.Column(db.String, nullable=False, default='')
    agent_name = db.Column(db.Integer, db.ForeignKey(AgentModel.name))
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


