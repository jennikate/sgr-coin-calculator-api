"""
Application configuration.
"""

###################################################################################################
# Imports
###################################################################################################


import os
from dotenv import load_dotenv


###################################################################################################
# Classes
###################################################################################################
load_dotenv()

class BaseConfig:
    """
    BaseConfig configuration settings.
    """

    DEBUG = os.getenv("DEBUG")
    ENV = os.getenv("FLASK_ENV") or "development"

    DB_USER = os.getenv("DBUSER")
    DB_PASSWORD = os.getenv("DBPASSWORD")
    DB_HOST = os.getenv("DBHOST")
    DB_PORT = os.getenv("DBPORT")
    DB_NAME = os.getenv("DBNAME")


    SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class TestingConfig(BaseConfig):
    """
    Testing configuration settings.
    """

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "postgresql://user:test@localhost/flaskdb"


config = {
    "production": BaseConfig, 
    "staging": BaseConfig, 
    "development": BaseConfig, 
    "testing": TestingConfig
    }


###################################################################################################
# End of file.
###################################################################################################
