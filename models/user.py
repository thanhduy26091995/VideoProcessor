from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# Define a model
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"<User {self.user_name}>"
