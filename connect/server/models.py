import datetime
import os

from connect.output import display
from connect.generate import digit_identifier, string_identifier
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Create a database engine and session
engine = create_engine('sqlite:///instance/connect.db')
Session = sessionmaker(bind=engine)

class ImplantModel(Base):
    __tablename__ = 'implants'

    id = Column(String, primary_key=True, default=digit_identifier)
    key = Column(String, unique=True, default=string_identifier)

    agents = relationship('AgentModel', backref='implant', lazy=True)

    def get_implant(self):
        return {
            'id': self.id,
            'key': self.key
        }


class AgentModel(Base):
    __tablename__ = 'agents'

    id = Column(String, primary_key=True, default=digit_identifier)
    check_in = Column(DateTime)
    check_in_task_id = Column(String, nullable=False, default=digit_identifier)
    _loaded_modules = Column(String)

    implant_key = Column(String, ForeignKey(ImplantModel.key))
    tasks = relationship('TaskModel', backref='agent', order_by='TaskModel.created')

    username = Column(String, nullable=False, default='•' * 4)
    hostname = Column(String, nullable=False, default='•' * 4)
    os = Column(String, nullable=False, default='•' * 4)
    ip = Column(String, nullable=False, default='•' * 4)
    integrity = Column(String, nullable=False, default='•' * 4)
    pid = Column(String, nullable=False, default='•' * 4)

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
        check_in_milliseconds = check_in_seconds * 1000
        check_in_minutes = check_in_seconds // 60
        check_in_hours = check_in_minutes // 60

        if check_in_milliseconds < 1000:
            return f'{check_in_milliseconds} ms'
        elif check_in_seconds < 60:
            return f'{check_in_seconds} sec'
        elif check_in_minutes < 60:
            return f'{check_in_minutes} min'
        else:
            return f'{check_in_hours} hr'

    def get_delta_seconds(self):
        if not self.check_in:
            return -1
        return int((datetime.datetime.now() - self.check_in).total_seconds())

    def get_agent(self):
        return {
            'id': self.id,
            'latency': self.get_delta(),
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
            session = Session()
            if task.delete_on_send:
                session.delete(task)
                session.close()
            session.commit()
        return batch_request


class TaskModel(Base):
    __tablename__ = 'tasks'

    id = Column(String, primary_key=True, default=digit_identifier)
    method = Column(String, nullable=False)
    created = Column(DateTime, nullable=False, default=datetime.datetime.now)
    type = Column(Integer, nullable=False)
    delete_on_send = Column(Boolean, default=False)

    _parameters = Column(String)
    _misc = Column(String)
    sent = Column(DateTime)
    completed = Column(DateTime)
    results = Column(Text)

    agent_id = Column(String, ForeignKey(AgentModel.id))

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


if not os.path.exists(f'{os.getcwd()}/instance/connect.db'):
    display('Database does not exist, creating it.', 'INFORMATION')
    Base.metadata.create_all(engine)
