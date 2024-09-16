from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# Define a model
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    name = db.Column(db.String(120), unique=False, nullable=True)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"<User {self.user_name}>"


class TransactionStatement(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.String(80), nullable=False)
    transaction_comment = db.Column(db.String(256), nullable=False)
    credit = db.Column(db.Float, nullable=False)
    offset_name = db.Column(db.String(256), nullable=False)


class TransactionStatement1(db.Model):
    __tablename__ = 'transactions_statement'

    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.String(80), nullable=False)
    transaction_comment = db.Column(db.String(256), nullable=False)
    credit = db.Column(db.Float, nullable=False)
    offset_name = db.Column(db.String(256), nullable=False)
