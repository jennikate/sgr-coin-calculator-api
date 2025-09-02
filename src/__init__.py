"""
This file is the entry point for the Flask application, providing the create_app() function that
returns the Flask application instance.
"""

###################################################################################################
#  Imports
###################################################################################################
import logging
from logging.handlers import RotatingFileHandler
import os

from dotenv import load_dotenv
from flask import Flask, current_app, jsonify
from flask_smorest import Api # type: ignore
from marshmallow import ValidationError # type: ignore

from src.extensions import db
from .api.v1.rank_routes import blp as RankBlueprint


###################################################################################################
#  Create App
###################################################################################################

def create_app(config_class=None):
    app = Flask(__name__)
    load_dotenv()

    # LOG LEVEL config
    # Remove default handler
    del app.logger.handlers[:]

    log_handler = logging.StreamHandler()
    # if want to log to file instead can use:
    # log_handler = RotatingFileHandler("flask_api_log.log", maxBytes=10000, backupCount=1)

    log_handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s"))
    app.logger.setLevel(logging.DEBUG) # levels used: DEBUG, INFO, WARNING, ERROR, CRITICAL
    app.logger.addHandler(log_handler)

    app.logger.debug(f"FLASK_ENV is {os.getenv('FLASK_ENV')}")
    app.logger.debug(f"Using config class: {config_class}")

    ## FLASK Config 
    # if an exception occurs hidden inside an extension of Flask, propogate it into the main app so we can see it
    app.config["PROPAGATE_EXCEPTIONS"] = True
    ## SMOREST Config
    app.config["API_TITLE"] = "SGR Coin Calculator REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    # SQLALCHEMY Config
    if config_class == "testing":
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("TEST_DATABASE_URL", "postgresql://test_user:test_password@localhost:5544/myapp_test")
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        app.config["TESTING"] = True
    # elif config_class == "production":
    #     app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    #     app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/myapp")
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        app.config["DEBUG"] = True


    # initialise and connect Flask app to SQLAlchemy
    db.init_app(app) 
    api = Api(app)


    # Register blueprints for smorest
    api.register_blueprint(RankBlueprint)
    
    app.logger.info(f"App created using DB: {app.config['SQLALCHEMY_DATABASE_URI']}")

    return app

###################################################################################################
#  End of file
###################################################################################################
