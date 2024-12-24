from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, ValidationError, validate
from flask_marshmallow import Marshmallow
from password import my_password


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://root:{my_password}@localhost/healthcenter_db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

class MemberSchema(ma.Schema):
    name = fields.String(required=True)
    age = fields.Integer(required=True)

    class Meta:
        fields = ("name", "age", "id")

class WorkoutSessionSchema(ma.Schema):
    session_date = fields.Date(required=True)
    session_time = fields.String(required=True)
    activity = fields.String(required=True)
    member_id = fields.Integer(required=True)

    class Meta:
        fields = ("session_date", "session_time", "activity", "member_id", "id")

member_schema = MemberSchema()
members_schema = MemberSchema(many=True)

workout_session_schema = WorkoutSessionSchema()
workout_sessions_schema = WorkoutSessionSchema(many=True)

# Models allow us to create tables in the database without writing the SQL in the database program directly
class Member(db.Model):
    __tablename__ = 'Members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    # The following db.relationship is creating a virtual relationship that is not visible on the database itself but is internally tracked
    # and allows us to quickly reference back to the Member model
    # This will create a collection of all the workouts from the WorkoutSession model and creates a virtual list of all workoutsessions for each member
    # You can loop through these now
    workouts = db.relationship('WorkoutSession', backref='member')

class WorkoutSession(db.Model):
    __tablename__ = 'Workouts'
    id = db.Column(db.Integer, primary_key=True)
    session_date = db.Column(db.Date, nullable=False)
    session_time = db.Column(db.String(55))
    activity = db.Column(db.String(355), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('Members.id'))



with app.app_context():
    db.create_all()

@app.route('/members', methods=['GET'])
def get_members():
    members = Member.query.all()
    return members_schema.jsonify(members)

@app.route('/members', methods=['POST'])
def add_member():
    try:
        member_data = member_schema.load(request.json)

    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_member = Member(name = member_data['name'],
                        age = member_data['age'])
    
    db.session.add(new_member)
    db.session.commit()
    return jsonify({'message': "New customer added successfully"}), 201

@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    member = Member.query.get_or_404(id)
    try:
        member_data = member_schema.load(request.json)
    
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    member.name = member_data['name']
    member.age = member_data['age']
    db.session.commit()
    return jsonify({'message': 'Customer updated successfully'}), 200

@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    member = Member.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({'message': 'Member deleted successfully'}),200

# -----------------------------------------------------------------------

@app.route('/workout_sessions', methods=['GET'])
def get_workouts():
    workouts = WorkoutSession.query.all()
    return workout_sessions_schema.jsonify(workouts)

@app.route('/workout_sessions', methods=['POST'])
def add_workout():
    try:
        workout_data = workout_session_schema.load(request.json)
    
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_workout = WorkoutSession(session_date = workout_data['session_date'],
                                 session_time = workout_data['session_time'],
                                 activity = workout_data['activity'],
                                 member_id = workout_data['member_id'])
    
    db.session.add(new_workout)
    db.session.commit()
    return jsonify({"message": "Workout added successfully."})


@app.route('/workout_sessions/<int:id>', methods=['PUT'])
def update_workout(id):
    workout = WorkoutSession.query.get_or_404(id)
    try:
        workout_data = workout_session_schema.load(request.json)

    except ValidationError as e:
        return jsonify(e.messages), 400
    workout.session_date = workout_data['session_date']
    workout.session_time = workout_data['session_time']
    workout.activity = workout_data['activity']
    workout.member_id = workout_data['member_id']
    db.session.commit()
    return jsonify({"message": "Workout updated successfully."}), 200

@app.route('/workout_sessions/<int:id>', methods=['DELETE'])
def delete_workout(id):
    workout = WorkoutSession.query.get_or_404(id)
    db.session.delete(workout)
    db.session.commit()
    return jsonify({'message': 'Workout removed successfully.'})

@app.route('/workout_sessions/by_member/<int:id>', methods = ['GET'])
def get_workout_by_member(id):

    workouts = WorkoutSession.query.filter_by(member_id=id).all()
    if workouts:
        return workout_sessions_schema.jsonify(workouts)
    else:
        return jsonify({"message": "No workouts found."}), 404

if __name__ == "__main__":
    app.run(debug=True)
