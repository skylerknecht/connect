from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Skyler(db.Model):
    id = db.Column(db.String, primary_key=True, default='lol')