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
#  Blueprints, extensions, etc.
###################################################################################################

def register_blueprints(app):
    app.register_blueprint(RankBlueprint)

###################################################################################################
#  Create App
###################################################################################################

def create_app(db_url=None):
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
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # initialise and connect Flask app to SQLAlchemy
    db.init_app(app) 
    api = Api(app)


    register_blueprints(app)
    app.logger.info("App created")

    return app

###################################################################################################
#  End of file
###################################################################################################
