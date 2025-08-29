"""
This file is the entry point for the Flask application, providing the create_app() function that
returns the Flask application instance.
"""

###################################################################################################
#  Imports
###################################################################################################
import os

from dotenv import load_dotenv
from flask import Flask

from src.api.v1.routes import bp # type: ignore
from src.extensions import db



def create_app(db_url=None):
    app = Flask(__name__)
    load_dotenv()

    ## Flask Config 
    # if an exception occurs hidden inside an extension of Flask, propogate it into the main app so we can see it
    app.config["PROPAGATE_EXCEPTIONS"] = True
    # SQLAlchemy Config
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # initialise and connect Flask app to SQLAlchemy
    db.init_app(app) 

    # # Register blueprints
    app.register_blueprint(bp)
    
    print("APP RUNNING")

    return app

###################################################################################################
#  End of file
###################################################################################################
