import datetime
import json

from connect.generate import digit_identifier, name_identifier
from connect.generate import generate_sleep, generate_jitter, generate_endpoints
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UserModel(db.model):
    # primary key
    name = db.Column(db.Integer, primary_key=True)

    
class ImplantModel(db.Model):
    # primary key
    name = db.Column(db.String, primary_key=True) 

    # properties
    key = db.Column(db.String, default=digit_identifier)
    language = db.Column(db.String, nullable=False)
   
    # properties with methods
    _available_modules = db.Column(db.String)
    _startup_commands = db.Column(db.String)
    _hardcoded_commands = db.Column(db.String)

    # relationships
    agents = db.relationship('AgentModel', backref='implant', lazy=True)

    def get_implant(self) -> dict:
        return {
            "key": self.key
        }

    
    # Available Modules

    @property
    def available_modules(self) -> dict:
        if not self._available_modules:
            return {}
        return json.loads(self._available_modules)

    @available_modules.setter
    def available_modules(self, value):
        self._available_modules = json.dumps(value)

        
    # Hardcoded Commands    

    @property
    def hardcoded_commands(self) -> list:
        if not self._hardcoded_commands:
            return []
        return [command for command in self._hardcoded_commands.split(',')]

    @hardcoded_commands.setter
    def hardcoded_commands(self, value):
        self._hardcoded_commands = value
        

    # Startup Commands    

    @property
    def startup_commands(self) -> list:
        if not self._startup_commands:
            return []
        return [command for command in self._startup_commands.split(',')]

    @startup_commands.setter
    def startup_commands(self, value):
        self._startup_commands = value

        
    # Supported Commands    

    @property
    def supported_commands(self) -> list:
        supported_commands = [command for command in self.hardcoded_commands]
        return supported_commands.extend(self.available_modules.keys())


class AgentModel(db.Model):
    # primary key
    name = db.Column(db.String, primary_key=True, default=name_identifier)

    # properties
    check_in = db.Column(db.DateTime, default=datetime.datetime.fromtimestamp(823879740.0))
    endpoints = db.Column(db.String, default=generate_endpoints)
    jitter = db.Column(db.String, default=generate_jitter)
    sleep = db.Column(db.String, default=generate_sleep)

    # properties with methods
    _loaded_modules = db.Column(db.String)

    # information
    hostname = db.Column(db.String, default='')
    ip = db.Column(db.String, default='')
    integrity = db.Column(db.String, default='')
    username = db.Column(db.String, default='')

    # relationships
    implant_key = db.Column(db.String, db.ForeignKey(ImplantModel.key))
    tasks = db.relationship('TaskModel', backref='agent', order_by='TaskModel.created')

    def get_agent(self):
        return {
            'name': self.name,
            'status': self.status,
            'supported_commands': self.implant.supported_commands,
            'loaded_modules': self.loaded_modules,
            'information': f'{self.username}@{self.hostname} ({self.ip}) [{self.integrity}]',
        }
    
    # Loaded Modules

    @property
    def loaded_modules(self) -> list:
        if not self._loaded_modules:
            return ''
        return [module for module in self._loaded_modules.split(',')]

    @loaded_modules.setter
    def loaded_modules(self, value):
        self._loaded_modules = value


    # Status

    @property
    def status(self) -> str:
        sleep = float(self.sleep)
        jitter = float(self.jitter)/100.0
        if str(self.check_in.timestamp()) == '823879740.0':
            return 'new'
        max_delay = sleep * jitter + sleep
        check_in_delta = (datetime.datetime.now() - self.check_in).total_seconds()
        if check_in_delta <= max_delay + 60.0:
            return 'connected'
        if  max_delay + 60.0 <= check_in_delta <= max_delay + 300.0:
            return 'stale'
        return 'disconnected'



class TaskModel(db.Model):
    # properties
    identifier = db.Column(db.Integer, primary_key=True, default=digit_identifier)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    type = db.Column(db.Integer, nullable=False)
    results = db.Column(db.Text, default='No results.')

    # properties with methods
    _arguments = db.Column(db.String, nullable=False, default='')
    
    # time properties
    created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    completed = db.Column(db.DateTime)
    sent = db.Column(db.DateTime)

    # relationships
    agent_name = db.Column(db.String, db.ForeignKey(AgentModel.name))

    
    # Arguments

    @property
    def arguments(self) -> list:
        return [str(x) for x in self._arguments.split(',')]

    @arguments.setter
    def arguments(self, value):
        self._arguments = value