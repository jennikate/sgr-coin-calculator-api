"""
Main entry point for the Flask application. This script creates the Flask application instance using
create_app()
"""

###################################################################################################
#  Imports
###################################################################################################

import os

from flask import logging
from flask_migrate import Migrate # type: ignore

from src import create_app
from api.models import db # type: ignore

###################################################################################################
#  Body
###################################################################################################
# NOTE: create_app is in src/__init__.py, and does the app config, blueprint registration, 
# db is defined in src/extensions.py

config_name = os.getenv("FLASK_ENV")
app = create_app(config_name)

migrate = Migrate(app, db)

# LOG LEVEL config
    # Remove default handler
del app.logger.handlers[:]

log_handler = logging.StreamHandler()
# if want to log to file instead can use:
# log_handler = RotatingFileHandler("flask_api_log.log", maxBytes=10000, backupCount=1)

log_handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s"))
app.logger.setLevel(logging.DEBUG) # levels used: DEBUG, INFO, WARNING, ERROR, CRITICAL
app.logger.addHandler(log_handler)

app.logger.info("App running")

# adding for when I get to the CORS parts, this is how it was done in our other projects
# from flask_cors import CORS (add flask_cors to project)
# CORS(app, resources={r"/*": {"origins": "*"}})


###################################################################################################
# Entry point
###################################################################################################


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")


###################################################################################################
# End of rile
###################################################################################################
