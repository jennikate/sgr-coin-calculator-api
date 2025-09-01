"""
This module defines flask-smorest resources for endpoints.

Endpoints:
 - /rank:
   - POST: Add a new rank
   - GET: Get all ranks

Classes:
 - RankResource: Resource for adding a rank.

"""

###################################################################################################
#  Imports
###################################################################################################

from flask.views import MethodView
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError # to catch db errors
from flask_smorest import Blueprint, abort # type: ignore

from api.models import RankModel
from api.schemas import MessageSchema, RankQueryArgsSchema, RankSchema

from src import db


###################################################################################################
#  Config
###################################################################################################
# TODO: consider moving Blueprint config to a separate file
# TODO: work out where the best place to put the url_prefix is

blp = Blueprint("rank", __name__, url_prefix="/v1", description="Rank operations")


###################################################################################################
#  Classes (flask-smorest resources)
###################################################################################################

@blp.route("/rank")
class RankResource(MethodView):
    """
    Resources for managing a rank.
    """
    @blp.arguments(RankSchema) # validate incoming JSON : will trigger an error response if invalid
    @blp.response(201, RankSchema) # serialize outgoing JSON
    def post(self, new_data):
        """
        Add a new rank
        """
        rank = RankModel(**new_data) # can do this as we've validated data with .arguments above

        try:
            db.session.add(rank)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred when inserting to db")
        except Exception as e:
            db.session.rollback()
            abort(500, message=str(e))

        return rank
    

    @blp.arguments(RankQueryArgsSchema, location="query")
    @blp.response(200, RankSchema(many=True)) # serialize outgoing JSON
    def get(self, args):
        """Get ranks by query parameters"""
        query = RankModel.query

        if "name" in args:
            checked = "name"
            query = query.filter_by(name=args["name"])
        if "position" in args:
            checked = "position"
            query = query.filter_by(position=args["position"])

        results = query.all()
        if not results:
            abort(404, message=f"No ranks found for {checked}: {args[checked]}")

        return results
    

@blp.route("/rank/<int:rank_id>")
class RankByIdResource(MethodView):
    """
    Resources for updating or deleting a rank by id.
    """
    @blp.response(200, RankSchema)
    def get(self, rank_id):
        """
        Get rank by id
        """
        rank = RankModel.query.get_or_404(rank_id)
        return rank
    
    @blp.arguments(RankSchema(partial=True)) # allow partial updates even though all fields required in schema
    @blp.response(200, RankSchema)
    def patch(self, update_data, rank_id):
        """
        Update rank partially by id
        """
        rank = RankModel.query.get_or_404(rank_id)

        if "name" in update_data:
            rank.name = update_data["name"]
        if "position" in update_data:
            rank.position = update_data["position"]
        if "share" in update_data:
            rank.share = update_data["share"]

        try:
            db.session.add(rank)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred when inserting to db")
        except Exception as e:
            db.session.rollback()
            abort(500, message=str(e))
        
        return rank

    @blp.response(200, MessageSchema)
    def delete(self, rank_id):
        """
        Delete rank by id
        """
        rank = RankModel.query.get_or_404(rank_id)

        try:
            db.session.delete(rank)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred when inserting to db")
        except Exception as e:
            db.session.rollback()
            abort(500, message=str(e))

        return { "message": f"Rank id {rank_id} deleted" }, 200

    
@blp.route("/ranks")
class RanksResource(MethodView):
    """
    Resources for getting all ranks.
    """
    @blp.response(200, RankSchema(many=True)) # serialize outgoing JSON
    def get(self):
        """
        Get all ranks
        """
        try:
            ranks = RankModel.query.order_by(RankModel.id).all()

        except SQLAlchemyError:
            abort(500, message="An error occurred when querying the db")
        except Exception as e:
            abort(500, message=str(e))

        return ranks



###################################################################################################
#  End of File
###################################################################################################
