from dotenv import load_dotenv
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from application.auth.user import db
from application.auth.user import user
from config import Config

# Load environment variables from a .env file
load_dotenv()


def create_app():
    app = Flask(__name__)
    # Load configuration
    app.config.from_object(Config)

    # Initialize the database
    db.init_app(app)
    Migrate(app, db)

    # Initialize JWT
    JWTManager(app)

    # Register Blueprint
    app.register_blueprint(user, url_prefix='/user')

    return app
