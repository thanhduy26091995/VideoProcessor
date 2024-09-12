from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config

# Load environment variables from a .env file
load_dotenv()

app = Flask(__name__)

# Load configuration
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# Initialize the database
with app.app_context():
    db.create_all()


# Define a model
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"<User {self.user_name}>"


# Route get all users
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{"id": user.id, "username": user.username, "email": user.email} for user in users])


# Register account
@app.route('/register', methods=['POST'])
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


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user_name = data['username']
    password = data['password']

    user = User.query.filter_by(user_name=user_name).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify(messsage="Invalid credentials"), 400

    #     Create access token
    access_token = create_access_token(identity=user.user_name)
    refresh_token = create_refresh_token(identity=user.user_name)
    return jsonify(access_token=access_token, refresh_token=refresh_token), 200


if __name__ == '__main__':
    app.run(debug=True)
