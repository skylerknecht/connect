import datetime
import json

from connect.generate import digit_identifier, name_identifier, string_identifier
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class ImplantModel(db.Model):
    # properties
    id = db.Column(db.String, primary_key=True, default=digit_identifier)
    name = db.Column(db.String, unique=True, nullable=False)
    key = db.Column(db.String, unique=True, default=string_identifier)

    # relationships
    agents = db.relationship('AgentModel', backref='implant', lazy=True)

    def get_implant(self):
        # return Implant(self.name, self.id, self.key, self.location)
        pass


class AgentModel(db.Model):
    # properties
    id = db.Column(db.Integer, primary_key=True, default=digit_identifier)
    check_in = db.Column(db.DateTime)
    check_in_task_id = db.Column(db.Integer, nullable=False, default=digit_identifier)

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

    def get_agent(self):
        # return Agent(self.name, str(self.check_in), self.username, self.hostname, self.ip, self.os,
        #             self.implant.options, self.implant.name)
        pass

    def get_tasks(self):
        batch_request = []
        for task in self.tasks:
            if task.sent:
                continue
            batch_request.append(task.get_task())
        return batch_request


class TaskModel(db.Model):
    # required properties
    id = db.Column(db.Integer, primary_key=True, default=digit_identifier)
    name = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    type = db.Column(db.Integer, nullable=False)

    # optional properties
    description = db.Column(db.String)
    _parameters = db.Column(db.String)
    scheduled = db.Column(db.DateTime)
    sent = db.Column(db.DateTime)
    completed = db.Column(db.DateTime)
    results = db.Column(db.Text)

    # relationships
    agent_id = db.Column(db.Integer, db.ForeignKey(AgentModel.id))

    @property
    def parameters(self):
        if not self._parameters:
            return []
        return [str(x) for x in self._parameters.split(',')]

    @parameters.setter
    def parameters(self, value):
        self._parameters = value

    def get_task(self):
        return {
            'method': self.name,
            'params': self.parameters,
            'id': self.id
        }
