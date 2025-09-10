"""
This defines the Marshmallow schemas for the API.

"""

###################################################################################################
#  Imports
###################################################################################################

from marshmallow import Schema, fields, validates, ValidationError # type: ignore
from sqlalchemy import select, exists

from src.api.models import MemberModel, RankModel # type: ignore
from src.extensions import db

###################################################################################################
#  Schemas
###################################################################################################

class MessageSchema(Schema):
    message = fields.String(required=True, metadata={"example": "Rank deleted successfully"})


## RANKS
class RankSchema(Schema):
    id = fields.UUID(dump_only=True)
    name = fields.Str(required=True, metadata={"description": "The name of the rank", "example": "Private"})
    position = fields.Int(required=True, metadata={"description": "The position of the rank", "example": 1})
    share = fields.Float(required=True, metadata={"description": "The share of the total pay allocated to this rank", "example": 0.50})
    
    include_relationships = False   # important! prevent recursive nesting

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


## MEMBERS
class BaseMemberSchema(Schema):
    id = fields.UUID(dump_only=True)
    name = fields.Str(required=True, metadata={"description": "The character name", "example": "John Doe"})
    status = fields.Bool(metadata={"description": "The member's status", "example": True}) # defaults to True if no value provided
    
    @validates('name')
    def validate_name(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("Name must not be empty.")
        if len(value) > 256:
            raise ValidationError("Name must not exceed 256 characters.")
        # Check DB for existing record using SQLAlchemy 2.0 style
        # Build a subquery that selects *something* from RankModel
        subq_exists = select(MemberModel.id).where(MemberModel.name == value).exists()
        # Wrap the EXISTS in a SELECT and execute
        exists_flag = db.session.execute(select(subq_exists)).scalar()
        if exists_flag:
            raise ValidationError(f"There is already a member with name {value}.")


class MemberSchema(BaseMemberSchema):
    rank_id = fields.UUID(required=True, load_only=True, metadata={"description": "The ID of the rank assigned to the member", "example": 1})
    rank = fields.Nested(RankSchema, dump_only=True)

    include_fk = True
    include_relationships = False   # prevent auto-adding rank again

    @validates('rank_id')
    def validate_rank_exists(self, value, **kwargs):
        subq_exists = select(RankModel.id).where(RankModel.id == value).exists()
        # Wrap the EXISTS in a SELECT and execute
        exists_flag = db.session.execute(select(subq_exists)).scalar()
        if not exists_flag:
            raise ValidationError(f"Rank {value} does not exist")


###################################################################################################
#  End of File
###################################################################################################
 