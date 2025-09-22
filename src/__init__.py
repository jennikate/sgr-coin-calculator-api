"""
This file is the entry point for the Flask application, providing the create_app() function that
returns the Flask application instance.
"""

###################################################################################################
#  Imports
###################################################################################################
import logging
import os
import secrets

from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate # type: ignore
from flask_smorest import Api # type: ignore
# from logging.handlers import RotatingFileHandler # used if we want to log to file

from config import config
from src.extensions import db
from .api.v1.job_routes import blp as JobBlueprint
from .api.v1.member_routes import blp as MemberBlueprint
from .api.v1.rank_routes import blp as RankBlueprint

###################################################################################################
#  Blueprints, extensions, etc.
###################################################################################################

def register_blueprints(api):
    api.register_blueprint(JobBlueprint)
    api.register_blueprint(MemberBlueprint)
    api.register_blueprint(RankBlueprint)
    

###################################################################################################
#  Create App
###################################################################################################

def create_app(config_name):
    app = Flask(__name__)

    # Only load dotenv if FLASK_ENV is not already set (e.g., in Docker)
    if not os.getenv("FLASK_ENV"):
        load_dotenv(".env.local")  # for host dev

    app.logger.debug('DEBUG')
    app.logger.info('INFO')

    # SECRET KEY CONFIG
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY") or secrets.token_hex(32)

    # LOGGING CONFIG
    log_level = logging.os.getenv("LOG_LEVEL", "INFO")
    # Remove default handler
    del app.logger.handlers[:]

    log_handler = logging.StreamHandler()
    # if want to log to file instead can use:
    # log_handler = RotatingFileHandler("flask_api_log.log", maxBytes=10000, backupCount=1)

    log_handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s"))
    app.logger.setLevel(log_level) # levels used: DEBUG, INFO, WARNING, ERROR, CRITICAL
    app.logger.addHandler(log_handler)

    app.logger.info("---------- starting create_app ----------")
    app.logger.info(f"Log level set to: {log_level}")
    app.logger.debug(f"Config name is: {config_name}")

    # load config from config.py
    app.config.from_object(config[config_name])
    ## commented out as this returns all the config vars, including sensitive ones.
    ## only use in development debugging and never in production
    # app.logger.debug(f"Config settings: {vars(config[config_name])}")

    # initialise and connect Flask app to SQLAlchemy
    db.init_app(app) 
    migrate = Migrate(app, db)
    api = Api(app)

    register_blueprints(api)
    app.logger.info("---------- create_app finished ----------")
    app.logger.info("Swagger UI available at http://localhost:5000/api/swagger-ui")
    app.logger.info(f"App running in {config_name} mode")

    return app

###################################################################################################
#  End of file
###################################################################################################
