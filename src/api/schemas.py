"""
This defines the Marshmallow schemas for the API.

"""

###################################################################################################
#  Imports
###################################################################################################

from marshmallow import Schema, fields, validates, ValidationError # type: ignore

from .models import RankModel # type: ignore
from src import db

###################################################################################################
#  Schemas
###################################################################################################

# We make a plain schema for each model to avoid circular imports
# These are setup now in anticipation of needing more complex schemas later

class PlainRankSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    position = fields.Int(required=True)
    share = fields.Float(required=True)

    @validates('name')
    def validate_name(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("Name must not be empty.")
        if len(value) > 20:
            raise ValidationError("Name must not exceed 20 characters.")
        
    @validates('position')
    def validate_position(self, value, **kwargs):
        if value <= 0:
            raise ValidationError("Position must be a positive integer.")
        # Check DB for existing record
        exists = db.session.query(
            db.exists().where(RankModel.position == value)
        ).scalar()

        if exists:
            raise ValidationError(f"There is already a rank at position {value}.")
        
    @validates('share')
    def validate_share(self, value, **kwargs):
        if value < 0:
            raise ValidationError("Share must be a non-negative float.")


class RankSchema(PlainRankSchema):
    pass

###################################################################################################
#  End of File
###################################################################################################
 