from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, ValidationError, validate
from password import my_password


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://root:{my_password}@localhost/healthcenter_db'
db = SQLAlchemy(app)


class Member(db.Model):
    __tablename__ = 'Members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=False)

class WorkoutSession(db.Model):
    __tablename__ = 'Workouts'
    session_id = db.Column(db.Integer, primary_key=True)
    session_date = db.Column(db.Date, nullable=False)
    session_time = db.Column(db.String(55), nullable=False)
    activity = db.Column(db.String(355), nullable=False)
    workout = db.relationship('WorkoutSession', backref='member')
    # TODO: Double check the above classes and be sure of the relationshipshhh 

with app.app_context():
    db.create_all()


