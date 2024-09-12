from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

# PostgreSQL Database configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://duyb:@localhost/myflaskdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init database
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Define a model
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"


# Route to add a new user
@app.route('/user', methods=['POST'])
def add_user():
    data = request.json
    new_user = User(username=data['username'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created"}), 201


# Route get all users
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{"id": user.id, "username": user.username, "email": user.email} for user in users])


if __name__ == '__main__':
    app.run(debug=True)
