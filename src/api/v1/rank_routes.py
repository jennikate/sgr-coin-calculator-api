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
from sqlalchemy.exc import IntegrityError, SQLAlchemyError # to catch db errors
from flask_smorest import Blueprint, abort # type: ignore

from api.models import RankModel
from api.schemas import RankSchema

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
            ranks = RankModel.query.all()
        except SQLAlchemyError:
            abort(500, message="An error occurred when querying the db")
        except Exception as e:
            abort(500, message=str(e))

        return ranks



###################################################################################################
#  End of File
###################################################################################################
