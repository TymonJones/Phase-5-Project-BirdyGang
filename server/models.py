from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates 
from datetime import datetime
# initializes database to link up with SQLAlchemy/ORMs 
db = SQLAlchemy()

class User(db.Model):
    __tablename__= 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    skill_level_id = db.Column(db.Integer, db.ForeignKey('skill_level.id'), nullable=False)

    # Validation: Ensure the username is unique
    @validates('username')
    def validate_username(self, key, value):
        existing_user = User.query.filter(User.username == value).first()
        if existing_user and existing_user.id != self.id:
            raise AssertionError('Username is already in use')
        return value

class SkillLevel(db.Model):
    __tablename__= 'skill_level'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    users = db.relationship('User', backref='skill_level', lazy=True)


    @validates('name')
    def validate_name(self, key, value):
        existing_skill_level = SkillLevel.query.filter(SkillLevel.name == value).first()
        if existing_skill_level and existing_skill_level.id != self.id:
            raise AssertionError('Must be: novice, intermediate, advanced')
        return value
    

class Course(db.Model):
    __tablename__= 'course'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    tee_times = db.relationship('TeeTime', backref='course', lazy=True)

class TeeTime(db.Model):
    __tablename__= 'tee_times'
    
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    
    
    @validates('date_time')
    def validate_date_time(self, key, value):
        if value <= datetime.now():
            raise AssertionError('Tee time must be in the future')
        return value
    
    
    
    
    
    
    # add validations to models
    # add constraints to columns 