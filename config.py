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

    ## FLASK Config 
    # if an exception occurs hidden inside an extension of Flask, propogate it into the main app so we can see it
    PROPAGATE_EXCEPTIONS = True
    ## SMOREST Config
    API_TITLE = "SGR Coin Calculator REST API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_URL_PREFIX = "/api"
    OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    # SQLALCHEMY Config
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
