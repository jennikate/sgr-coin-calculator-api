"""
Constants for use across the app.
"""

###################################################################################################
#  Imports
###################################################################################################

import os

from dotenv import load_dotenv
from uuid import UUID

###################################################################################################
#  Constants
###################################################################################################

load_dotenv()

COMPANY_CUT = os.getenv("COMPANY_CUT", 0.1) # default to 10% if no value in env file

# NOTE: the values for DEFAULT_RANK must be the same as in the database
# which is seeded with the values from this migration -> *_add_default_rank.py
# see docs/creation-notes#Creating and updating the db for more details
DEFAULT_RANK = {
    "id": UUID("11111111-1111-1111-1111-111111111111"),
    "name": "default",
    "position": 99,
    "share": 0
}


###################################################################################################
#  End of file
###################################################################################################
