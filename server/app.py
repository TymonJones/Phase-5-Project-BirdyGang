from dotenv import dotenv_values
from flask import Flask, request, jsonify, session, abort, make_response
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from models import db, User, SkillLevel, Course, TeeTime
from flask_restful import Api, Resource 
from flask_cors import CORS
from faker import Faker
import random
# install bcrypt into environment 
# passlib if bcrypt doesnt work!

fake = Faker()

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
migrate = Migrate(app,db)
db.init_app(app)
api = Api(app)


# generate secret key => import secrets, ecrets.token_hex(16)
# load_env()
# ENV = dotenv_values()

ENV = dotenv_values('../env') 
app.secret_key = ENV["SECRET_KEY"]

# Set up migrations

# Create a new user
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    # Check if the skill level exists
    skill_level = SkillLevel.query.get(data['skill_level_id'])
    if skill_level is None:
        return jsonify({'message': 'Skill level not found'}), 404
    
    new_user = User(username=data['username'], password=data['password'], skill_level_id=data['skill_level_id'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

# Get all users
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_data = [{'id': user.id, 'username': user.username, 'skill_level': user.skill_level.name} for user in users]
    return jsonify(users_data), 200

# Get a specific user
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'message': 'User not found'}), 404
    user_data = {'id': user.id, 'username': user.username, 'skill_level': user.skill_level.name}
    return jsonify(user_data), 200

# Update a user
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'message': 'User not found'}), 404
    
    data = request.get_json()
    user.username = data['username']
    user.skill_level_id = data['skill_level_id']
    db.session.commit()
    return jsonify({'message': 'User updated successfully'}), 200

# Delete a user
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'message': 'User not found'}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200



# Login Route
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and bcrypt.check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

# Logout Route
@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logout successful'}), 200

# Search Route
@app.route('/search/courses', methods=['GET'])
def search_courses():
    location = request.args.get('location')
    name = request.args.get('name')

    # Query the database based on user input
    courses = Course.query.filter(
        (Course.location.like(f'%{location}%')) | (Course.name.like(f'%{name}%'))
    ).all()

    return jsonify({'courses': [course.serialize() for course in courses]}), 200


# Courses routes
@app.route('/api/courses', methods=['GET'])
def get_courses():
    try:
        courses = Course.query.all()

        course_data = [{'id': course.id, 'name': course.name, 'location': course.location} for course in courses]

        
        return jsonify(course_data), 200
    
    except Exception as e:
       
        
        return jsonify({'error': 'An error occurred while fetching golf courses.'}), 500

@app.route('/api/sample-courses', methods=['GET'])
def get_sample_courses():
    num_courses = int(request.args.get('num', 10))  # allow specifying the number of courses
    sample_courses = generate_sample_golf_courses(num_courses)
    return jsonify(sample_courses)


def generate_sample_golf_courses(num_courses=10):
    sample_courses = []
    for _ in range(num_courses):
        course = {
            'name': fake.company(),
            'location': fake.address(),
            'par': random.randint(60, 72),
            'rating': round(random.uniform(3.0, 5.0), 1),
            'holes': random.choice([9, 18]),
        }
        sample_courses.append(course)
    return sample_courses


        # Query the database to fetch all golf courses
        # Create a list of dictionaries with course information
        # Return the data as JSON
        # Handle any errors that may occur during the database query


# Booking Route
@app.route('/book/teetime', methods=['POST'])
def book_tee_time():
    data = request.json
    start_time = data.get('start_time')
    course_id = data.get('course_id')
    user_id = session.get('user_id')  # Assuming user is authenticated

    # Check if the tee time is available (add validation logic)

    new_tee_time = TeeTime(start_time=start_time, course_id=course_id, user_id=user_id)
    db.session.add(new_tee_time)
    db.session.commit()

    return jsonify({'message': 'Tee time booked successfully'}), 201

# User Tee Times Route
@app.route('/user/teetimes', methods=['GET'])
def user_tee_times():
    user_id = session.get('user_id')  # Assuming user is authenticated
    user_tee_times = TeeTime.query.filter_by(user_id=user_id).all()
    
    return jsonify({'tee_times': [tee_time.serialize() for tee_time in user_tee_times]}), 200

# Pairing Algo ??
def pair_users_by_skill_level(user_id):
    user = User.query.get(user_id)
    user_skill_level = user.skill_level_id

    # Find other users with similar skill levels
    similar_users = User.query.filter_by(skill_level_id=user_skill_level).filter(User.id != user_id).all()

    return similar_users

# Pairing Route
@app.route('/pair', methods=['GET'])
def pair_users():
    user_id = session.get('user_id')  # Assuming user is authenticated
    similar_users = pair_users_by_skill_level(user_id)

    return jsonify({'similar_users': [user.username for user in similar_users]}), 200


if __name__ == '__main__':
    app.run(port=5555,debug=True)