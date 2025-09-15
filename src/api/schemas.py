"""
This defines the Marshmallow schemas for the API.

"""

###################################################################################################
#  Imports
###################################################################################################

from marshmallow import Schema, fields, post_load, validates, ValidationError # type: ignore
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field 
from sqlalchemy import select, exists
# TODO: refactor schemas to use the marshmallow_sqlalchemy meta pattern (see JobMemberSchema)


from src.api.models import JobModel, MemberJobModel, MemberModel, RankModel # type: ignore
from src.extensions import db

###################################################################################################
#  Schemas
###################################################################################################

class MessageSchema(Schema):
    message = fields.String(required=True, metadata={"example": "Rank deleted successfully"})

class WholeNumber(fields.Field):
    """
    Optional whole number field that rejects decimals.
    This is to offset the fact that Marshmallow will coerce floats into ints
    and we would rather force the user to supply an int
    """

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return None
        try:
            # Allow integers, reject floats with decimal part
            if isinstance(value, float) and value != int(value):
                raise ValidationError("Value cannot have decimals.")
            return int(value)
        except (ValueError, TypeError):
            raise ValidationError("Value must be a whole number.")

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


class MemberQueryArgsSchema(Schema):
    rank = fields.UUID(required=False, metadata={"description": "Filter by rank id"})


# JOBS
class MemberJobRequestSchema(SQLAlchemySchema):
    class Meta:
        model = MemberJobModel
        load_instance = False  # only validate json, return a dict
        # load_instance = True tells Marshmallow: “I want to deserialize JSON directly into SQLAlchemy model instances.”
        # in PATCH cases it's considered safer to not do that because you often merge or update objects manually, not blindly load new instances.
        
    member_id = auto_field(required=True)
    member_pay = auto_field()


class MemberJobResponseSchema(SQLAlchemySchema):
    class Meta:
        model = MemberJobModel
        load_instance = True

    member_id = auto_field()
    member_rank = auto_field(dump_only=True)
    member_pay = auto_field()


class BaseJobSchema(Schema):
    id = fields.UUID(dump_only=True)
    job_name = fields.Str(required=True, allow_none=False, metadata={"description": "A short name for a job", "example": "Ogres in Hinterlands"})
    job_description = fields.Str(metadata={"description": "An optional longer description", "example": "For Stromgarde, collecting horns for bounty"})
    start_date = fields.Date(required=True, metadata={"description": "The date of the job, or the start date if a multiday job", "example": "2025-04-23"})
    end_date = fields.Date(metadata={"description": "Optional end date for multiday jobs", "example": "2025-04-28"})
    total_silver = WholeNumber(metadata={"Description": "Total amount paid in silver", "example": 100})

    @validates("job_name")
    def validate_job_name(self, value, **kwargs):
        if isinstance(value, str) and value.strip() == "":
            raise ValidationError("job_name must not be empty.")
        if len(value) > 100:
            raise ValidationError("job_name must not exceed 100 characters.")
        
    @validates('job_description')
    def validate_job_description(self, value, **kwargs):
        if len(value) > 256:
            raise ValidationError("job_description must not exceed 256 characters.")
        
    @validates('total_silver')
    def validate_total_silver(self, value, **kwargs):
        if value < 0:
            raise ValidationError("total_silver cannot be a negative value.")


class JobUpdateSchema(SQLAlchemySchema):
    class Meta:
        model = JobModel
        load_instance = False  # only return dict, no automatic model instance

    job_name = auto_field()
    job_description = auto_field()
    start_date = auto_field()
    end_date = auto_field()
    total_silver = auto_field()

    members = fields.List(fields.Nested(MemberJobRequestSchema))
    remove_members = fields.List(fields.UUID(), load_only=True)


class JobResponseSchema(SQLAlchemySchema):
    class Meta:
        model = JobModel
        load_instance = True

    id = auto_field(dump_only=True)
    job_name = auto_field()
    job_description = auto_field()
    start_date = auto_field()
    end_date = auto_field()
    total_silver = auto_field()
    member_jobs = fields.List(fields.Nested(MemberJobResponseSchema))


class JobQueryArgsSchema(Schema):
    start_date = fields.Date(required=False, metadata={"description": "Filter by start date"})
        

###################################################################################################
#  End of File
###################################################################################################
 