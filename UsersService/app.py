import datetime

from flask import Flask
from UsersService.database import db, User
from UsersService.urls import DEFAULT_DB
from UsersService.views import blueprints


def create_app(database=DEFAULT_DB, wtf=False, login_disabled=False):
    flask_app = Flask(__name__)
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_SECRET_KEY'] = 'A SECRET KEY'
    flask_app.config['SECRET_KEY'] = 'ANOTHER ONE'
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = database
    flask_app.config['WTF_CSRF_ENABLED'] = wtf
    flask_app.config['LOGIN_DISABLED'] = login_disabled

    for bp in blueprints:
        flask_app.register_blueprint(bp)
        bp.app = flask_app

    db.init_app(flask_app)
    db.create_all(app=flask_app)

    with flask_app.app_context():
        q = db.session.query(User).filter(User.email == 'example@example.com')
        user = q.first()
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

        q = db.session.query(User).filter(User.email == 'cantagallo@example.com')
        user = q.first()
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

    return flask_app

app = create_app()
