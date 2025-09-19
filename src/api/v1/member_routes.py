"""
This module defines flask-smorest resources for endpoints.

Endpoints:
 - /member:
   - POST: Add a new member
   - GET: Get a members by id or get all members
   - PATCH: Update a member with parital or full data
   - DELETE: Delete a member

- /members:
    - GET: Get all members

Classes:
 - MemberResource: Resource for creating a member.
 - MemberByIdResource: Resource for managing a specific member by ID.
 - AllMembersResource: Resource for getting all members.

"""

## Detailed commentary is on the rank_routes.py file, check there if anything is unclear.

###################################################################################################
#  Imports
###################################################################################################

from flask import current_app
from flask.views import MethodView
from sqlalchemy import asc
from sqlalchemy.exc import SQLAlchemyError # to catch db errors
from flask_smorest import Blueprint, abort # type: ignore
from uuid import UUID

from src.api.models import MemberModel, RankModel # type: ignore
from src.api.schemas import MemberSchema, MessageSchema, MemberQueryArgsSchema

from src.extensions import db


###################################################################################################
#  Config
###################################################################################################

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
        current_app.logger.debug("---------------- STARTING POST NEW MEMBER --------------")
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

        current_app.logger.debug(f"Created member: {member}")
        current_app.logger.debug("---------------- FINISHED POST NEW JOB --------------")
        return member
    


@blp.route("/member/<member_id>")
class MemberByIdResource(MethodView):
    """
    Resources for updating or deleting a member by id.
    """
    @blp.response(200, MemberSchema)
    def get(self, member_id):
        """
        Get member by id
        """
        current_app.logger.debug("---------------- STARTING GET MEMBER BY ID --------------")
        current_app.logger.debug(f"Getting member id: {member_id}")
        try:
            data = UUID(member_id)  # converts string to UUID object
        except ValueError:
            abort(400, message="Invalid member id")

        member = MemberModel.query.get_or_404(data)

        current_app.logger.debug(f"Getting member: {member}")
        current_app.logger.debug("---------------- FINISHED GET MEMBER BY ID --------------")
        return member
        

    @blp.arguments(MemberSchema(partial=True)) # allow partial updates even though all fields required in schema
    @blp.response(200, MemberSchema)
    def patch(self, update_data, member_id):
        """
        Update member partially by id
        """
        current_app.logger.debug("---------------- STARTING PATCH MEMBER BY ID --------------")
        current_app.logger.debug(f"Patching member id: {member_id}")
        current_app.logger.debug(f"Patching data: {update_data}")
        try:
            data = UUID(member_id)  # converts string to UUID object
        except ValueError:
            abort(400, message="Invalid member id")

        member = MemberModel.query.get_or_404(data)

        if "name" in update_data:
            member.name = update_data["name"]
        if "rank_id" in update_data:
            member.rank_id = update_data["rank_id"]
        if "active" in update_data:
            member.active = update_data["active"]

        try:
            db.session.add(member)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred when inserting to db")
        except Exception as e:
            db.session.rollback()
            abort(500, message=str(e))
        
        current_app.logger.debug(f"Returning member: {member}")
        current_app.logger.debug("---------------- FINISHED PATCH MEMBER --------------")
        return member
    

    @blp.response(200, MessageSchema)
    def delete(self, member_id):
        """
        Delete member by id
        """
        current_app.logger.debug("---------------- STARTING DELETE MEMBER BY ID --------------")
        current_app.logger.debug(f"Deleting member id: {member_id}")
        try:
            data = UUID(member_id)  # converts string to UUID object
        except ValueError:
            abort(400, message="Invalid member id")

        member = MemberModel.query.get_or_404(data)

        try:
            db.session.delete(member)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred when inserting to db")
        except Exception as e:
            db.session.rollback()
            abort(500, message=str(e))

        current_app.logger.debug(f"Deleted member: {member_id}")
        current_app.logger.debug("---------------- FINISHED DELETE MEMBER BY ID --------------")
        return { "message": f"Member id {member_id} deleted" }, 200


@blp.route("/members")
class AllMemberssResource(MethodView):
    """
    Resource for getting all members.
    """
    @blp.arguments(MemberQueryArgsSchema, location="query")
    @blp.response(200, MemberSchema(many=True))
    def get(self, args):
        """
        Get all members
        """
        current_app.logger.debug("---------------- STARTING GET ALL MEMBERS --------------")
        current_app.logger.debug(f"Getting members with args: {args}")
        query = MemberModel.query.join(MemberModel.rank)

        # Apply filter if provided
        # Apply filter only if the argument exists
        rank_id = args.get("rank")  # Matches the schema field name
        if rank_id is not None:
            query = query.filter(MemberModel.rank_id == rank_id)

        # Apply sorting
        members = query.order_by(
            RankModel.position.asc(),
            MemberModel.name.asc()
        ).all()


        current_app.logger.debug(f"Returning members: {members}")
        current_app.logger.debug("---------------- FINISHED GET ALL MEMBERS --------------")
        return members

###################################################################################################
#  End of File
###################################################################################################
