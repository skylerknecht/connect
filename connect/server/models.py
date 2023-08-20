import datetime

from connect.output import display
from connect.generate import digit_identifier, string_identifier
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class ImplantModel(db.Model):
    # properties
    id = db.Column(db.String, primary_key=True, default=digit_identifier)
    key = db.Column(db.String, unique=True, default=string_identifier)

    # relationships
    agents = db.relationship('AgentModel', backref='implant', lazy=True)

    def get_implant(self):
        return {
            'id': self.id,
            'key': self.key
        }


class AgentModel(db.Model):
    # properties
    id = db.Column(db.String, primary_key=True, default=digit_identifier)
    check_in = db.Column(db.DateTime)
    check_in_task_id = db.Column(db.String, nullable=False, default=digit_identifier)

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

    def get_delta(self):
        if not self.check_in:
            return 'Not Connected'
        check_in_seconds = int((datetime.datetime.now() - self.check_in).total_seconds())
        check_in_minutes = check_in_seconds // 60
        check_in_hours = check_in_minutes // 60
        return f'{check_in_seconds} Second(s)' if check_in_seconds <= 60 else f'{check_in_minutes} Minute(s)' if \
            check_in_minutes <= 60 else f'{check_in_hours} Hour(s)'

    def get_agent(self):
        return {
            'id': self.id,
            'time': self.get_delta(),
            'username': self.username,
            'os': self.os,
            'ip': self.ip,
            'integrity': self.integrity,
            'pid': self.pid
        }

    def get_tasks(self):
        batch_request = []
        for task in self.tasks:
            if task.sent:
                continue
            display(f'Sending task {task.method} to {task.agent.id}', 'INFORMATION')
            batch_request.append(task.get_task())
            task.sent = datetime.datetime.now()
            db.session.commit()
        return batch_request


class TaskModel(db.Model):
    # required properties
    id = db.Column(db.String, primary_key=True, default=digit_identifier)
    method = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    type = db.Column(db.Integer, nullable=False)

    # optional properties
    _parameters = db.Column(db.String)
    _misc = db.Column(db.String)
    sent = db.Column(db.DateTime)
    completed = db.Column(db.DateTime)
    results = db.Column(db.Text)

    # relationships
    agent_id = db.Column(db.String, db.ForeignKey(AgentModel.id))

    @property
    def parameters(self):
        if not self._parameters:
            return []
        return [str(x) for x in self._parameters.split(',')]

    @parameters.setter
    def parameters(self, value):
        self._parameters = value

    @property
    def misc(self):
        if not self._misc:
            return []
        return [str(x) for x in self._misc.split(',')]

    @misc.setter
    def misc(self, value):
        self._misc = value

    def get_task(self):
        return {
            'method': self.method,
            'params': self.parameters,
            'id': self.id
        }
