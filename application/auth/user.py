from flask import Blueprint, request
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import generate_password_hash, check_password_hash

from application.response import create_response
from models.user import db, User

user = Blueprint('user', __name__)


@user.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    user_name = data.get('username')
    password = data.get('password')
    # Validate value before processing
    if not user_name or not user_name or not password:
        return create_response(message="Please enter valid data", code=400)

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(user_name=user_name, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return create_response(message="User created", code=201)


@user.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user_name = data['username']
    password = data['password']

    current_user = User.query.filter_by(user_name=user_name).first()

    if not user or not check_password_hash(current_user.password, password):
        return create_response(message="Invalid credentials", code=400)

    #     Create access token
    access_token = create_access_token(identity=current_user.user_name)
    refresh_token = create_refresh_token(identity=current_user.user_name)
    return create_response(message="Login successfully", code=200, data={
        "access_token": access_token,
        "refresh_token": refresh_token
    })


# Route get all users
@user.route('/get_all', methods=['GET'])
def get_users():
    users = User.query.all()
    return create_response(message="Fetch list successfully", code=200,
                           data=[{"id": user.id, "username": user.user_name, "email": user.email} for user in users])
