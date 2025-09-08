"""
This module defines flask-smorest resources for endpoints.

Endpoints:
 - /rank:
   - POST: Add a new member
   - GET: Get a members by name, position, or id
   - PATCH: Update a member with parital or full data
   - DELETE: Delete a member

- /members:
    - GET: Get all members

Classes:
 - MemberResource: Resource for CRUD a member.
 - MemberByIdResource: Resource for getting a member by ID.
 - AllMembersResource: Resource for getting all members.

"""

## Detailed commentary is on the rank_routes.py file, check there if anything is unclear.

###################################################################################################
#  Imports
###################################################################################################

from flask import current_app
from flask.views import MethodView
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError # to catch db errors
from flask_smorest import Blueprint, abort # type: ignore

from src.api.models import MemberModel # type: ignore
from src.api.schemas import MemberSchema, MessageSchema

from src.extensions import db


###################################################################################################
#  Config
###################################################################################################
# TODO: consider moving Blueprint config to a separate file
# TODO: work out where the best place to put the url_prefix is

blp = Blueprint("member", __name__, url_prefix="/v1", description="Operations on members")


###################################################################################################
#  Classes (flask-smorest resources)
###################################################################################################

@blp.route("/member")
class MemberResource(MethodView):
    """
    Resources for managing a member.
    """
    @blp.arguments(MemberSchema)
    @blp.response(201, MemberSchema)
    def post(self, new_data):
        """
        Add a new member
        """
        current_app.logger.debug(f"Creating member with data: {new_data}")
        try:
            member = MemberModel(**new_data)
            db.session.add(member)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred when inserting to db")
        except Exception as e:
            db.session.rollback()
            abort(500, message=str(e))

        return member
    

@blp.route("/members")
class AllMemberssResource(MethodView):
    """
    Resource for getting all ranks.
    """
    @blp.response(200, MemberSchema(many=True))
    def get(self):
        """
        Get all ranks
        """
        ranks = MemberModel.query.all()
        return ranks

###################################################################################################
#  End of File
###################################################################################################
