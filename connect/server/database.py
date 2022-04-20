import datetime

from connect.server import db, generate_id


class Connections(db.Model):
    identifier = db.Column(db.Integer, primary_key=True, default=generate_id)
    check_in = db.Column(db.DateTime)
    requested = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    parent_id = db.Column(db.Integer, db.ForeignKey('connections.identifier'))
    type = db.Column(db.String, nullable=False)
    jobs = db.relationship('Jobs', backref='connection', lazy=True)
    children = db.relationship('Connections', backref=db.backref('parent', remote_side=[identifier]), lazy=True)

    def get_list(self):
        return [self.check_in, len(self.jobs), self.type]


class Jobs(db.Model):
    identifier = db.Column(db.Integer, primary_key=True, default=generate_id)
    name = db.Column(db.String, nullable=False)
    arguments = db.Column(db.String, nullable=False, default='')
    connection_id = db.Column(db.Integer, db.ForeignKey('connections.identifier'), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    completed = db.Column(db.DateTime)
    type = db.Column(db.Integer, nullable=False)
    results = db.Column(db.Text, default='No results.')

    def get_list(self):
        if self.completed:
            return [self.name, self.connection_id, 'completed', self.completed, self.results]
        return [self.name, self.connection_id, 'created', self.created, self.results]


class Routes(db.Model):
    identifier = db.Column(db.Integer, primary_key=True, default=generate_id)
    name = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String, nullable=False, default='No description.')

    def get_list(self):
        return [self.name, self.description]
