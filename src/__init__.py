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
from flask_migrate import Migrate # type: ignore
from flask_smorest import Api # type: ignore

from config import config
from src.extensions import db
from .api.v1.rank_routes import blp as RankBlueprint
from .api.v1.member_routes import blp as MemberBlueprint

###################################################################################################
#  Blueprints, extensions, etc.
###################################################################################################

def register_blueprints(api):
    api.register_blueprint(RankBlueprint)
    api.register_blueprint(MemberBlueprint)
    

###################################################################################################
#  Create App
###################################################################################################

def create_app(config_name):
    app = Flask(__name__)
    load_dotenv()

    # LOGGING CONFIG
    # Remove default handler
    del app.logger.handlers[:]

    log_handler = logging.StreamHandler()
    # if want to log to file instead can use:
    # log_handler = RotatingFileHandler("flask_api_log.log", maxBytes=10000, backupCount=1)

    log_handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s"))
    app.logger.setLevel(logging.DEBUG) # levels used: DEBUG, INFO, WARNING, ERROR, CRITICAL
    app.logger.addHandler(log_handler)

    app.logger.debug("---------- starting create_app ----------")
    app.logger.debug(f"Config name is: {config_name}")
    # app.logger.debug(f"DB URI: {os.getenv('DATABASE_URL')}")

    # load config from config.py
    app.config.from_object(config[config_name])
    app.logger.debug(f"Config settings: {vars(config[config_name])}")

    # initialise and connect Flask app to SQLAlchemy
    db.init_app(app) 
    migrate = Migrate(app, db)
    api = Api(app)

    register_blueprints(api)
    app.logger.info("---------- create_app finished ----------")

    return app

###################################################################################################
#  End of file
###################################################################################################
