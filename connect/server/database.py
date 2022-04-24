import datetime

from connect.server import db, generate_id


class Connections(db.Model):
    identifier = db.Column(db.Integer, primary_key=True, default=generate_id)
    check_in = db.Column(db.DateTime)
    requested = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    parent_id = db.Column(db.Integer, db.ForeignKey('connections.identifier'))
    type = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False, default='....')
    hostname = db.Column(db.String, nullable=False, default='....')
    os = db.Column(db.String, nullable=False, default='....')
    jobs = db.relationship('Jobs', backref='connection', lazy=True)
    children = db.relationship('Connections', backref=db.backref('parent', remote_side=[identifier]), lazy=True)

    def get_list(self):
        return [self.check_in, self.type, self.username, self.hostname, self.os]


class Jobs(db.Model):
    identifier = db.Column(db.Integer, primary_key=True, default=generate_id)
    name = db.Column(db.String, nullable=False)
    _arguments = db.Column(db.String, nullable=False, default='')
    connection_id = db.Column(db.Integer, db.ForeignKey('connections.identifier'), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    completed = db.Column(db.DateTime)
    sent = db.Column(db.DateTime)
    type = db.Column(db.Integer, nullable=False)
    results = db.Column(db.Text, default='No results.')

    def get_list(self):
        if self.completed:
            return [self.name, self.connection_id, 'Completed', self.completed, self.results]
        if self.sent:
            return [self.name, self.connection_id, 'Sent', self.sent, self.results]
        return [self.name, self.connection_id, 'Created', self.created, self.results]

    @property
    def arguments(self):
        return str([str(x) for x in self._arguments.split(',')])

    @arguments.setter
    def arguments(self, value):
        self._arguments = value


class Routes(db.Model):
    identifier = db.Column(db.Integer, primary_key=True, default=generate_id)
    name = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String, nullable=False, default='No description.')

    def get_list(self):
        return [self.name, self.description]
