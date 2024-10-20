from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin

# Naming conventions for the database
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)

class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    difficulty = db.Column(db.Integer, nullable=False)

    # Relationship: An Activity has many Signups
    signups = db.relationship('Signup', back_populates='activity', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'difficulty': self.difficulty,
        }

    def __repr__(self):
        return f'<Activity {self.id}: {self.name}>'

class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer, nullable=False)

    # Relationship: A Camper has many Signups
    signups = db.relationship('Signup', back_populates='camper', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'signups': [signup.to_dict() for signup in self.signups]  # Include signups here
        }

    @validates('name')
    def validate_name(self, key, name):
        if name is None or name == '':
            raise ValueError("Camper must have a name.")
        return name

    @validates('age')
    def validate_age(self, key, age):
        if age < 8 or age > 18:
            raise ValueError("Camper age must be between 8 and 18.")
        return age

    def __repr__(self):
        return f'<Camper {self.id}: {self.name}>'

class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer, nullable=False)

    # Foreign keys
    camper_id = db.Column(db.Integer, db.ForeignKey('campers.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False)

    # Relationships
    camper = db.relationship('Camper', back_populates='signups')
    activity = db.relationship('Activity', back_populates='signups')

    def to_dict(self):
        return {
            'id': self.id,
            'time': self.time,
            'camper_id': self.camper_id,
            'activity_id': self.activity_id,
            'activity': self.activity.name,  # Include activity name
            'camper': self.camper.name  # Include camper name
        }

    @validates('time')
    def validate_time(self, key, time):
        if time < 0 or time > 23:
            raise ValueError("Signup time must be between 0 and 23.")
        return time

    def __repr__(self):
        return f'<Signup {self.id}>'
