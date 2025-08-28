import os

from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate # type: ignore

from db import db
import models

def create_app(db_url=None):
    app = Flask(__name__)
    load_dotenv()

    print("DBenv", os.getenv("DATABASE_URL"))
    print ("DB db", db)

    ## Flask Config 
    # if an exception occurs hidden inside an extension of Flask, propogate it into the main app so we can see it
    app.config["PROPAGATE_EXCEPTIONS"] = True
    # SQLAlchemy Config
    
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app) # initialise and connect Flask app to SQLAlchemy
    migrate = Migrate(app, db)



    # a simple page that says hello
    @app.route('/bob')
    def hello():
        return 'Hello, World!'
    
    print("APP RUNNING")

    return app
