"""
Main entry point for the Flask application. This script creates the Flask application instance using
create_app()
"""

###################################################################################################
#  Imports
###################################################################################################
import os

from flask_migrate import Migrate # type: ignore

from src import create_app
from api.models import db # type: ignore

###################################################################################################
#  Body
###################################################################################################

config_name = os.getenv("FLASK_ENV")
app = create_app(config_name)

migrate = Migrate(app, db)

# adding for when I get to the CORS parts, this is how it was done in our other projects
# from flask_cors import CORS (add flask_cors to project)
# CORS(app, resources={r"/*": {"origins": "*"}})


###################################################################################################
# Entry point
###################################################################################################


if __name__ == "__main__":
    app.run("0.0.0.0")


###################################################################################################
# End of rile
###################################################################################################
