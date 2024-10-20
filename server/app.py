#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''


# Campers Routes
@app.route('/campers', methods=['GET'])
def get_campers():
    campers = Camper.query.all()
    # Explicitly define the structure to exclude 'signups'
    return jsonify([{
        'id': camper.id,
        'name': camper.name,
        'age': camper.age
    } for camper in campers]), 200


@app.route('/campers/<int:id>', methods=['GET'])
def get_camper_by_id(id):
    camper = Camper.query.get(id)
    if camper is None:
        return jsonify({"error": "Camper not found"}), 404
    return jsonify(camper.to_dict()), 200


@app.route('/campers', methods=['POST'])
def create_camper():
    data = request.get_json()
    try:
        if 'name' not in data or 'age' not in data:
            raise ValueError("Missing name or age")
        age = int(data['age'])
        if age < 8 or age > 18:
            raise ValueError("Age must be between 8 and 18")
        
        camper = Camper(name=data['name'], age=age)
        db.session.add(camper)
        db.session.commit()
        return jsonify(camper.to_dict()), 201
    except ValueError as e:
        return jsonify({"errors": [str(e)]}), 400


@app.route('/campers/<int:id>', methods=['PATCH'])
def update_camper(id):
    camper = Camper.query.get(id)
    if camper is None:
        return jsonify({"error": "Camper not found"}), 404

    data = request.get_json()
    try:
        if 'name' in data:
            if not data['name']:
                raise ValueError("Name cannot be empty")
            camper.name = data['name']
        
        if 'age' in data:
            age = int(data['age'])
            if age < 8 or age > 18:
                raise ValueError("Age must be between 8 and 18")
            camper.age = age
        
        db.session.commit()
        return jsonify(camper.to_dict()), 202
    except ValueError as e:
        return jsonify({"errors": ["validation errors"]}), 400


@app.route('/campers/<int:id>', methods=['DELETE'])
def delete_camper(id):
    camper = Camper.query.get(id)
    if camper is None:
        return jsonify({"error": "Camper not found"}), 404
    
    db.session.delete(camper)
    db.session.commit()
    return '', 204


# Activities Routes
@app.route('/activities', methods=['GET'])
def get_activities():
    activities = Activity.query.all()
    return jsonify([activity.to_dict() for activity in activities]), 200


@app.route('/activities/<int:id>', methods=['DELETE'])
def delete_activity(id):
    activity = Activity.query.get(id)
    if activity is None:
        return jsonify({"error": "Activity not found"}), 404
    
    db.session.delete(activity)
    db.session.commit()
    return '', 204


# Signups Routes
@app.route('/signups', methods=['POST'])
def create_signup():
    data = request.get_json()
    try:
        if 'camper_id' not in data or 'activity_id' not in data or 'time' not in data:
            raise ValueError("Missing camper_id, activity_id or time")

        time = int(data['time'])
        if time < 0 or time > 23:
            raise ValueError("Time must be between 0 and 23")
        
        signup = Signup(camper_id=data['camper_id'], activity_id=data['activity_id'], time=time)
        db.session.add(signup)
        db.session.commit()
        return jsonify(signup.to_dict()), 201
    except ValueError as e:
        return jsonify({"errors": ["validation errors"]}), 400


if __name__ == '__main__':
    app.run(port=5555, debug=True)
