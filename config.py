import os

from dotenv import load_dotenv

# Print to check if they are loaded
load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = os.getenv('FLASK_ENV') == 'development'
