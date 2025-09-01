"""
This defines the Marshmallow schemas for the API.

"""

###################################################################################################
#  Imports
###################################################################################################

from marshmallow import Schema, fields, validates, ValidationError # type: ignore
from sqlalchemy import select, exists

from .models import RankModel # type: ignore
from src import db

###################################################################################################
#  Schemas
###################################################################################################

class MessageSchema(Schema):
    message = fields.String(required=True, metadata={"example": "Rank deleted successfully"})


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
        # Check DB for existing record using SQLAlchemy 2.0 style
        # Build a subquery that selects *something* from RankModel
        subq_exists = select(RankModel.id).where(RankModel.name == value).exists()
        # Wrap the EXISTS in a SELECT and execute
        exists_flag = db.session.execute(select(subq_exists)).scalar()
        if exists_flag:
            raise ValidationError(f"There is already a rank with name {value}.")
        
    @validates('position')
    def validate_position(self, value, **kwargs):
        if value <= 0:
            raise ValidationError("Position must be a positive integer.")
        # Check DB for existing record : easier to read way, but less performant
        exists = db.session.query(RankModel).filter_by(position=value).first() is not None
        if exists:
            raise ValidationError(f"There is already a rank at position {value}.")
        
    @validates('share')
    def validate_share(self, value, **kwargs):
        if value < 0:
            raise ValidationError("Share must be a non-negative float.")
        
    
class RankQueryArgsSchema(Schema):
    name = fields.String(required=False, metadata={"description": "Filter by rank name"})
    position = fields.Integer(required=False,  metadata={"description": "Filter by rank position"})

class RankSchema(PlainRankSchema):
    pass

###################################################################################################
#  End of File
###################################################################################################
 