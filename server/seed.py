# from faker import Faker
from app import app
from models import db, User, SkillLevel, Course, TeeTime
from datetime import datetime


# ** Questions **
# db.init_app(app)
# with app.app_context():??
# fake.name() to generate demo user names */
# will I create a circular reference if I use serialize() vs SerializerMixin


# fake = Faker()


def seed_data():
    with app.app_context():
        # Seed SkillLevels
        skill_levels = [
            {'name': 'Beginner'},
            {'name': 'Intermediate'},
            {'name': 'Advanced'}
        ]
        for level_data in skill_levels:
            existing_skill_level = SkillLevel.query.filter_by(name=level_data['name']).first()
            if existing_skill_level:
                skill_level = existing_skill_level
            else:
                skill_level = SkillLevel(**level_data)
            db.session.add(skill_level)

        # Seed Users
        users = [
            {'username': 'user1', 'password': 'password123', 'skill_level_id': 1},
            {'username': 'user2', 'password': 'password456', 'skill_level_id': 2},
            {'username': 'user3', 'password': 'password789', 'skill_level_id': 3},
        ]
        for user_data in users:
            user = User(**user_data)
            db.session.add(user)

        # Seed Courses
        courses = [
            {'name': 'Golf Course A', 'location': 'Location A'},
            {'name': 'Golf Course B', 'location': 'Location B'},
        ]
        for course_data in courses:
            course = Course(**course_data)
            db.session.add(course)

        # Seed TeeTimes
        tee_times = [
            {'start_time': datetime(2023, 8, 15, 8, 0), 'course_id': 1},
            {'start_time': datetime(2023, 8, 16, 9, 0), 'course_id': 2},
        ]
        for tee_time_data in tee_times:
            tee_time = TeeTime(**tee_time_data)
            db.session.add(tee_time)

        db.session.commit()

if __name__ == '__main__':
    seed_data()
