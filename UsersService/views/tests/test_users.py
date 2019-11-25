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
            user = db.session.query(User).filter(User.email == 'example@example.com').first()
            if user is None:
                example = User()
                example.firstname = 'Admin'
                example.lastname = 'Admin'
                example.email = 'example@example.com'
                example.dateofbirth = datetime.datetime(2010, 10, 5)
                example.is_admin = True
                example.set_password('admin')
                db.session.add(example)
                db.session.commit()
            
            user = db.session.query(User).filter(User.email == 'cantagallo@example.com').first()
            if user is None:
                example = User()
                example.firstname = 'Cantagallo'
                example.lastname = 'Rooster'
                example.email = 'cantagallo@example.com'
                example.dateofbirth = datetime.datetime(2010, 10, 10)
                example.is_admin = True
                example.set_password('p')
                db.session.add(example)
                db.session.commit()

            user = db.session.query(User).filter(User.email == 'thebest@example.com').first()
            if user is None:
                example = User()
                example.firstname = 'Cantagallo'
                example.lastname = 'TheBest'
                example.email = 'thebest@example.com'
                example.dateofbirth = datetime.datetime(2010, 10, 8)
                example.is_admin = True
                example.set_password('p')
                db.session.add(example)
                db.session.commit()

            user = db.session.query(User).filter(User.email == 'theworst@example.com').first()
            if user is None:
                example = User()
                example.firstname = 'TheWorst'
                example.lastname = 'Rooster'
                example.email = 'theworst@example.com'
                example.dateofbirth = datetime.datetime(2010, 10, 2)
                example.is_admin = True
                example.set_password('p')
                db.session.add(example)
                db.session.commit()

    # Executed at end of each test
    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()

    
    def test_all_users(self):
        reply = self.client.get('/users')
        body = json.loads(str(reply.data, 'utf8'))
        self.assertEqual(body, [
            {"email": "example@example.com", "firstname": "Admin", "id": 1, "lastname": "Admin"},
            {"email": "cantagallo@example.com", "firstname": "Cantagallo", "id": 2, "lastname": "Rooster"},
            {"email": "thebest@example.com", "firstname": "Cantagallo", "id": 3, "lastname": "TheBest"},
            {"email": "theworst@example.com", "firstname": "TheWorst", "id": 4, "lastname": "Rooster"}
        ])

    #TODO
    '''def test_create_user(self):
        # Correct request
        data = json.dumps({
            'firstname'     : 'Prova',
            'lastname'      : 'Prova',
            'dateofbirth'   :  datetime.datetime(2010, 10, 5).strftime('%d/%m/%Y'),
            'email'         : 'Prova',
            'password'      : 'Prova'
        })
        reply = self.client.post('/users/create', data=data)
        self.assertEqual(reply.status_code, 201)

        user = db.session.query(User).filter(User.email == 'Prova').first()
        self.assertnotNone(user)


        # TODO: Email address already used
        data = json.dumps({
            'firstname'     : 'Natalia',
            'lastname'      : 'Prova',
            'dateofbirth'   :  datetime.datetime(2010, 10, 5).strftime('%d/%m/%Y'),
            'email'         : 'cantagallo@example.com',
            'password'      : 'Prova'
        })
        reply = self.client.post('/users/create', data=data)
        self.assertEqual(reply.status_code, 406)

        # Date of birth > today
        data = json.dumps({
            'firstname'     : 'Prova',
            'lastname'      : 'Prova',
            'dateofbirth'   :  datetime.datetime(3000, 10, 5).strftime('%d/%m/%Y'),
            'email'         : 'Prova',
            'password'      : 'Prova'
        })
        reply = self.client.post('/users/create', data=data)
        self.assertEqual(reply.status_code, 400)
        #self.assertEqual(reply.text, 'Date of birth can not be greater than today')

        # TODO: Bad parameters'''


    def test_login(self):
        # Correct request
        query_string = 'email=cantagallo@example.com&password=p'
        reply = self.client.post('/users/login?'+query_string)
        self.assertEqual(reply.status_code, 200)

        # Password uncorrect
        query_string = 'email=cantagallo@example.com&password=wrong'
        reply = self.client.post('/users/login?'+query_string)
        self.assertEqual(reply.status_code, 400)
        #self.assertEqual(reply.text, 'Password uncorrect')

        # Email does not exist
        query_string = 'email=wrong&password=p'
        reply = self.client.post('/users/login?'+query_string)
        self.assertEqual(reply.status_code, 404)

        # Bad parameters
        query_string = 'email=cantagallo@example.com'
        reply = self.client.post('/users/login?'+query_string)
        self.assertEqual(reply.status_code, 400)
        #self.assertEqual(reply.text, 'Error with one parameter')

    def test_user_data(self):
        # Correct request
        reply = self.client.get('users/1')
        body = json.loads(str(reply.data, 'utf8'))
        self.assertEqual(body, {
            'dateofbirth': '05/10/2010', 'email': 'example@example.com',
            'firstname': 'Admin', 'follower_counter': 0, 'id': 1,
            'is_admin': True, 'lastname': 'Admin'
        })

        # User does not exist
        reply = self.client.get('users/6')
        self.assertEqual(reply.status_code, 404)

    def test_follow(self):
        # Requests with bad parameters
        reply = self.client.post('users/1/follow?current_user_id=')
        self.assertEqual(reply.status_code, 400)
        #self.assertEqual(reply.text, 'Error with current_user_id parameter')

        reply = self.client.post('users/1/follow?current_user_id=aa')
        self.assertEqual(reply.status_code, 400)
        #self.assertEqual(reply.text, 'Error with current_user_id parameter')

        # The user to follow does not exist
        reply = self.client.post('users/6/follow?current_user_id=2')
        self.assertEqual(reply.status_code, 404)
        #self.assertEqual(reply.text, 'The specified userid does not exist')

        # The follower does not exists
        reply = self.client.post('users/1/follow?current_user_id=8')
        self.assertEqual(reply.status_code, 404)
        #self.assertEqual(reply.text, 'The specified current_user_id does not exist')

        # The user try to follow himself
        reply = self.client.post('users/1/follow?current_user_id=1')
        self.assertEqual(reply.status_code, 400)
        #self.assertEqual(reply.text, 'A user can't follow himself')

        # Correct request
        reply = self.client.post('users/1/follow?current_user_id=2')
        self.assertEqual(reply.status_code, 200)
        #TODO: check if follower_counter has been incremented

        # Try to follow again the same user
        reply = self.client.post('users/1/follow?current_user_id=2')
        self.assertEqual(reply.status_code, 400)
        #self.assertEqual(reply.text, 'The user already follow this storyteller')

    def test_unfollow(self):
        # Requests with bad parameters
        reply = self.client.post('users/1/unfollow?current_user_id=')
        self.assertEqual(reply.status_code, 400)
        #self.assertEqual(reply.text, 'Error with current_user_id parameter')

        reply = self.client.post('users/1/unfollow?current_user_id=aa')
        self.assertEqual(reply.status_code, 400)
        #self.assertEqual(reply.text, 'Error with current_user_id parameter')

        # The user to follow does not exist
        reply = self.client.post('users/6/unfollow?current_user_id=2')
        self.assertEqual(reply.status_code, 404)
        #self.assertEqual(reply.text, 'The specified userid does not exist')

        # The follower does not exists
        reply = self.client.post('users/1/unfollow?current_user_id=8')
        self.assertEqual(reply.status_code, 404)
        #self.assertEqual(reply.text, 'The specified current_user_id does not exist')

        # The user try to unfollow himself
        reply = self.client.post('users/1/unfollow?current_user_id=1')
        self.assertEqual(reply.status_code, 400)
        #self.assertEqual(reply.text, 'A user can't unfollow himself')

        # Let user 2 follows user 1
        reply = self.client.post('users/1/follow?current_user_id=2')
        self.assertEqual(reply.status_code, 200)

        # Correct request
        reply = self.client.post('users/1/unfollow?current_user_id=2')
        self.assertEqual(reply.status_code, 200)
        #TODO: check if follower_counter has been decremented

        # Try to unfollow again the same user
        reply = self.client.post('users/1/unfollow?current_user_id=2')
        self.assertEqual(reply.status_code, 400)
        #self.assertEqual(reply.text, 'TThe user should follow the other user before unfollowing')

    def test_followers(self):
        # Let user 2 follows user 1
        reply = self.client.post('users/1/follow?current_user_id=2')
        self.assertEqual(reply.status_code, 200)

        # Get user 1 followers
        reply = self.client.get('users/1/followers')
        body = json.loads(str(reply.data, 'utf8'))
        self.assertEqual(body, [
            {"email": "cantagallo@example.com", "firstname": "Cantagallo", "id": 2, "lastname": "Rooster"}
        ])

        # The user does not exist
        reply = self.client.get('users/8/followers')
        self.assertEqual(reply.status_code, 404)

    def test_search_exist_firstname(self):
        response = self.client.get('/search?query=Admin')
        body = json.loads(str(response.data, 'utf8'))
        self.assertEqual(body, [
            {"email": "example@example.com", "firstname": "Admin", "id": 1, "lastname": "Admin"}])

    def test_search_exist_lastname(self):
        response = self.client.get('/search?query=TheBest')
        body = json.loads(str(response.data, 'utf8'))
        self.assertEqual(body, [
            {"email": "thebest@example.com", "firstname": "Cantagallo", "id": 3, "lastname": "TheBest"}])
    
    def test_search_double_exist_firstname(self):
        response = self.client.get('/search?query=Cantagallo')
        body = json.loads(str(response.data, 'utf8'))
        self.assertEqual(body, [
            {"email": "cantagallo@example.com", "firstname": "Cantagallo", "id": 2, "lastname": "Rooster"},
            {"email": "thebest@example.com", "firstname": "Cantagallo", "id": 3, "lastname": "TheBest"}])

    def test_search_double_exist_lastname(self):
        response = self.client.get('/search?query=Rooster')
        body = json.loads(str(response.data, 'utf8'))
        self.assertEqual(body, [
            {"email": "cantagallo@example.com", "firstname": "Cantagallo", "id": 2, "lastname": "Rooster"},
            {"email": "theworst@example.com", "firstname": "TheWorst", "id": 4, "lastname": "Rooster"}])

    def test_search_not_exist(self):
        response = self.client.get('/search?query=notexist')
        self.assertStatus(response, 204)

    def test_search_bad_request(self):
        # NO parameter
        response = self.client.get('/search?=notexist')
        body = json.loads(str(response.data, 'utf8'))

        self.assertStatus(response, 400)
        self.assertEqual(body['description'],
                         'Error with query parameter')

        # Wrong parameter
        response = self.client.get('/search?notquery=notexist')
        body = json.loads(str(response.data, 'utf8'))

        self.assertStatus(response, 400)
        self.assertEqual(body['description'],
                         'Error with query parameter')
    
    def test_search_empty_request(self):
        response = self.client.get('/search?query=')        
        self.assertStatus(response, 204)