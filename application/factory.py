from dotenv import load_dotenv
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from application.auth.user import db
from application.auth.user import user
from application.response import create_response
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
    jwt = JWTManager(app)

    # Register Blueprint
    app.register_blueprint(user, url_prefix='/user')

    @jwt.unauthorized_loader
    def custom_unauthorized_response(error):
        return create_response(message="Request does not contain an access token.", code=401)

    return app
