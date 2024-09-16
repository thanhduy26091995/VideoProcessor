from flask import Blueprint, request
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import jwt_required, get_jwt_identity
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

    # Query to check exist account first
    current_user = User.query.filter_by(user_name=user_name)
    if current_user:
        return create_response(message="User already exists", code=400)

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
@jwt_required()
def get_users():
    users = User.query.all()
    return create_response(message="Fetch list successfully", code=200,
                           data=[{"id": user.id, "username": user.user_name, "email": user.email} for user in users])


# Get user info
@user.route('/info', methods=['GET'])
@jwt_required()
def get_user_info():
    # Get the identity of the current user from the token
    current_user_name = get_jwt_identity()
    # Fetch user details from the database
    current_user = User.query.filter_by(user_name=current_user_name).first()

    # Validate
    if not current_user:
        return create_response(message="No user found", code=400)

    user_info = {
        "user_name": current_user.user_name,
        "email": current_user.email,
        "name": current_user.name
    }

    return create_response(message="Get user info successfully", code=200, data=user_info)


# Update user info
@user.route('/update_info', methods=['PUT'])
@jwt_required()
def update_user_info():
    data = request.get_json()
    email = data.get("email")
    name = data.get("name")

    # Get user_name from JWT
    current_user_name = get_jwt_identity()
    current_user = User.query.filter_by(user_name=current_user_name).first()
    if not current_user:
        return create_response(message="No user found", code=400)

    # Update value for user
    if email:
        current_user.email = email

    if name:
        current_user.name = name

    try:
        db.session.commit()
        return create_response(message="Update user info successfully", code=200)
    except Exception as e:
        db.session.rollback()
        return create_response(message="Failed to update user", code=500, data={"error": str(e)})
