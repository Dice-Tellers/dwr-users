import datetime

from flask import Blueprint
from flask import jsonify, request, abort, make_response
from UsersService.database import db, User, Follower

users = Blueprint('users', __name__)


# Returns the list of all users
@users.route('/users')
def _users():
    usrs = db.session.query(User)
    return jsonify([user.serialize() for user in usrs])


# Create a new user
@users.route('/users/create', methods=['POST'])
def _create_user():    
    try:
        user_data = request.get_json(request)

        # check user existence
        q = db.session.query(User).filter(User.email == user_data['email'])
        user = q.first()
        if user is not None:
            abort('406', 'The email address is already being used')
        # check date of birth < today
        dateofbirth = datetime.strptime(user_data['dateofbirth'], '%d/%m/%Y').date()
        if dateofbirth < date.today():
            abort('400', 'Date of birth can be greater than today')
        
        # create new user
        new_user = User()
        new_user.firstname = user_data['firstname']
        new_user.lastname = user_data['lastname']
        new_user.email = user_data['email']
        new_user.dateofbirth = dateofbirth
        new_user.is_admin = False
        new_user.set_password(user_data['password'])
        db.session.add(new_user)
        db.session.commit()
    # If values in request body aren't well-formed
    except ValueError:
        abort('404', 'Error with one parameters')

    return make_response("New user created", 201)


# Returns informations about a user
@users.route('/users/<int:userid>', methods=['GET'])
def _wall(userid):
    """ Ci pensa l'API gateway a differenziare tra my wall e other user wall,
         le informazioni vanno restituite tutte """
    q = db.session.query(User).filter(User.id == userid)
    user = q.first()

    # Check user existence
    if user is None:
        abort(404, 'The specified userid does not exist')
    # Returns user wall
    else:
        return jsonify(user.serialize_all())


# Fai eguire un utente da un altro utente (TODO:tradurre)
@users.route('/users/<int:id_user>/follow', methods=['POST'])
def _follow_user(id_user):
    current_user_id = -1
    try:
        current_user_id = int(request.args.get('current_user_id'))
    except Exception:
        abort(400, "Error with current_user_id parameter")

    if id_user == current_user_id:
        abort(400, "A user can't follow himself")
    if not _check_user_existence(id_user):
        abort(404, 'The specified userid does not exist')
    if not _check_user_existence(current_user_id):
        abort(404, 'The specified current_user_id does not exist')
    if _check_follower_existence(current_user_id, id_user):
        abort(400, "The user already follow this storyteller")

    new_follower = Follower()
    new_follower.follower_id = current_user_id
    new_follower.followed_id = id_user

    # add follower to database
    db.session.add(new_follower)
    db.session.query(User).filter_by(id=id_user).update({'follower_counter': User.follower_counter + 1})
    db.session.commit()

    return make_response("User followed", 200)


# Fai smettere di seguire un utente da un altro utente (TODO:tradurre)
@users.route('/users/<int:id_user>/unfollow', methods=['POST'])
def _unfollow_user(id_user):
    current_user_id = -1
    try:
        current_user_id = int(request.args.get('current_user_id'))
    except Exception:
        abort(400, "Error with current_user_id parameter")

    if id_user == current_user_id:
        abort(400, "A user can't unfollow himself")
    if not _check_user_existence(id_user):
        abort(404, 'The specified userid does not exist')
    if not _check_user_existence(current_user_id):
        abort(404, 'The specified current_user_id does not exist')
    if not _check_follower_existence(current_user_id, id_user):
        abort(400, "The user should follow the other user before unfollowing")

    Follower.query.filter_by(follower_id=current_user_id, followed_id=id_user).delete()
    db.session.query(User).filter_by(id=id_user).update({'follower_counter': User.follower_counter - 1})
    db.session.commit()

    return make_response("User unfollowed", 200)


# Returns the list of users followed by a user
@users.route('/users/<int:id_user>/followers', methods=['GET'])
def _followers(id_user):
    # Check user existence
    if not _check_user_existence(id_user):
        abort(404, 'The specified userid does not exist')
    else:
        usrs = User.query.join(Follower, User.id == Follower.follower_id).filter_by(followed_id=id_user)
        return jsonify([user.serialize() for user in usrs])        


# Returns True if the user identified by id_user exists
def _check_user_existence(id_user):
    user = db.session.query(User).filter(User.id == id_user)
    return user.first() is not None

# Returns True if the user identified by follower_id follows the user identified by followed_id
def _check_follower_existence(follower_id, followed_id):
    follower = db.session.query(Follower).filter_by(follower_id=follower_id, followed_id=followed_id)
    return follower.first() is not None
