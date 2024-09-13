from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import generate_password_hash, check_password_hash

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
        return jsonify(message="Please enter valid data"), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(user_name=user_name, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify(message="User created")


@user.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user_name = data['username']
    password = data['password']

    current_user = User.query.filter_by(user_name=user_name).first()

    if not user or not check_password_hash(current_user.password, password):
        return jsonify(messsage="Invalid credentials"), 400

    #     Create access token
    access_token = create_access_token(identity=current_user.user_name)
    refresh_token = create_refresh_token(identity=current_user.user_name)
    return jsonify(access_token=access_token, refresh_token=refresh_token), 200


# Route get all users
@user.route('/get_all', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{"id": user.id, "username": user.username, "email": user.email} for user in users])
