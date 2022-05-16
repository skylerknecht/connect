import datetime

from connect.generate import digit_identifier, name_identifier
from connect.generate import generate_sleep, generate_jitter, generate_endpoints
from connect.output import Agent, Stager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class StagerModel(db.Model):
    name = db.Column(db.String, primary_key=True)
    endpoint = db.Column(db.Integer, nullable=True)
    delivery = db.Column(db.String, nullable=False)

    def get_stager(self):
        return Stager(self.name, self.endpoint, self.delivery)


class ImplantModel(db.Model):
    # properties
    key = db.Column(db.String, primary_key=True, default=digit_identifier)
    sleep = db.Column(db.String, default=generate_sleep)
    jitter = db.Column(db.String, default=generate_jitter)
    endpoints = db.Column(db.String, default=generate_endpoints)
    _commands = db.Column(db.String, default='')

    # relationships
    agents = db.relationship('AgentModel', backref='implant', lazy=True)

    @property
    def commands(self):
        return [str(x) for x in self._commands.split(',')]

    @commands.setter
    def commands(self, value):
        self._commands = value


class AgentModel(db.Model):
    # properties
    name = db.Column(db.String, primary_key=True, default=name_identifier)
    check_in = db.Column(db.DateTime, default=datetime.datetime.fromtimestamp(823879740.0))
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
    jobs = db.relationship('JobModel', backref='agent', lazy=True)

    def get_agent(self):
        return Agent(self.name, str(self.check_in), self.username, self.hostname, self.pid, self.integrity,
                     self.implant.commands, self.sleep, self.jitter)


class JobModel(db.Model):
    identifier = db.Column(db.Integer, primary_key=True, default=digit_identifier)
    name = db.Column(db.String, nullable=False)
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


