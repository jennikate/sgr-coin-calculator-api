"""
Main entry point for the Flask application. This script creates the Flask application instance using
create_app()
"""

###################################################################################################
#  Imports
###################################################################################################

import os

from dotenv import load_dotenv
# from flask_migrate import Migrate # type: ignore

from src import create_app
from src.extensions import db # type: ignore

###################################################################################################
#  Body
###################################################################################################
# NOTE: create_app is in src/__init__.py, and does the app config, blueprint registration, 
# db is defined in src/extensions.py

load_dotenv()
config_name = os.getenv("FLASK_ENV", "production")
app = create_app(config_name)
app.logger.debug(f"Config name is: {config_name}")


app.logger.info("---------- run.py finished ----------")


# adding for when I get to the CORS parts, this is how it was done in our other projects
# from flask_cors import CORS (add flask_cors to project)
# CORS(app, resources={r"/*": {"origins": "*"}})


###################################################################################################
# Entry point
###################################################################################################

debug_mode = os.getenv("DEBUG", False)

if __name__ == "__main__":
    app.logger.info(f"Running in debug mode? {debug_mode}")
    app.run(debug=debug_mode, host="0.0.0.0")


###################################################################################################
# End of file
###################################################################################################
