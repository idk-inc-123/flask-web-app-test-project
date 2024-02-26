from . import db
from flask_login import UserMixin

class Genres(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)


class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text)
    genre = db.Column(db.Integer, db.ForeignKey('genres.id'))
    author = db.Column(db.String(255))
    publish_date = db.Column(db.String(255))
    price = db.Column(db.DECIMAL(10, 2))
    stock = db.Column(db.Integer)

    genre_rel = db.relationship('Genres')


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
