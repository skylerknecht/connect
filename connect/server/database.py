import random

from connect.server import db


def generate_id():
    new_id = [str(random.randint(1, 9)) for _ in range(0, 10)]
    new_id = ''.join(new_id)
    return new_id


class Connections(db.Model):
    identifier = db.Column(db.Integer, primary_key=True, default=generate_id)
    check_in = db.Column(db.DateTime)
    parent_id = db.Column(db.Integer, db.ForeignKey('connections.identifier'))
    jobs = db.relationship('Jobs', backref='connection', lazy=True)
    children = db.relationship('Connections', backref=db.backref('parent', remote_side=[identifier]), lazy=True)

    def get_list(self):
        return [self.check_in, len(self.jobs)]


class Jobs(db.Model):
    identifier = db.Column(db.Integer, primary_key=True, default=generate_id)
    name = db.Column(db.String, nullable=False)
    arguments = db.Column(db.String, nullable=False, default='')
    connection_id = db.Column(db.Integer, db.ForeignKey('connections.identifier'), nullable=False)
    status = db.Column(db.String, nullable=False, default='created')
    results = db.Column(db.Text, default='No results.')

    def get_list(self):
        return [self.name, self.connection_id, self.status, self.results]


class Routes(db.Model):
    identifier = db.Column(db.Integer, primary_key=True, default=generate_id)
    name = db.Column(db.String, unique=True, nullable=False)

    def get_list(self):
        return [self.name]
