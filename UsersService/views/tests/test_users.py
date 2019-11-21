import datetime
import json

import flask_testing
from flask import jsonify

from UsersService.app import create_app
from UsersService.database import db, User, Follower
from UsersService.urls import TEST_DB



class TestUsers(flask_testing.TestCase):
    app = None

    # First thing called
    def create_app(self):
        global app
        app = create_app(database=TEST_DB)
        return app

    # Set up database for testing
    def setUp(self) -> None:
        with app.app_context():
            # Create two users
            example = User()
            example.firstname = 'Admin'
            example.lastname = 'Admin'
            example.email = 'example@example.com'
            example.dateofbirth = datetime.datetime(2010, 10, 5)
            example.is_admin = True
            example.set_password('admin')
            db.session.add(example)
            db.session.commit()
            
            example = User()
            example.firstname = 'Cantagallo'
            example.lastname = 'Rooster'
            example.email = 'cantagallo@example.com'
            example.dateofbirth = datetime.datetime(2010, 10, 10)
            example.is_admin = True
            example.set_password('p')
            db.session.add(example)
            db.session.commit()



    # Executed at end of each test
    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()

    
    def test_all_users(self):
        response = self.client.get('/users')
        body = json.loads(str(response.data, 'utf8'))
        data = json.dumps([
            {"email": "example@example.com", "firstname": "Admin", "id": 1, "lastname": "Admin"},
            {"email": "cantagallo@example.com", "firstname": "Cantagallo", "id": 2, "lastname": "Rooster"}
        ])
        self.assertEqual(body, data)
