"""
This module defines flask-smorest resources for endpoints.

Endpoints:
 - /job:
   - POST: Add a new job
   - GET: Get a job by id, date, or get all jobs
   - PATCH: Update a job with parital or full data
   - DELETE: Delete a job

- /jobs:
    - GET: Get all jobs

Classes:
 - JobResource: Resource for creating a job.
 - JobByIdResource: Resource for managing a job by ID.
 - AllJobssResource: Resource for getting all jobs.

"""

###################################################################################################
#  Imports
###################################################################################################

from datetime import date
from flask import current_app
from flask.views import MethodView
from sqlalchemy import asc
from sqlalchemy.exc import SQLAlchemyError # to catch db errors
from flask_smorest import Blueprint, abort # type: ignore
from uuid import UUID

from src.api.models import JobModel, MemberModel, RankModel # type: ignore
from src.api.schemas import JobSchema, MemberSchema, MessageSchema

from src.extensions import db


###################################################################################################
#  Config
###################################################################################################
# TODO: consider moving Blueprint config to a separate file
# TODO: work out where the best place to put the url_prefix is

blp = Blueprint("job", __name__, url_prefix="/v1", description="Operations on jobs")


###################################################################################################
#  Classes (flask-smorest resources)
###################################################################################################

@blp.route("/job")
class JobResource(MethodView):
    """
    Resources for creating a job.
    """
    @blp.arguments(JobSchema)
    @blp.response(201, JobSchema)
    def post(self, new_data):
        """
        Add a new job
        """
        current_app.logger.debug(f"Creating job with data: {new_data}")

        try:
            job = JobModel(**new_data)
            # NOTE: we do not need to reformat dates from strings to Python date format here
            # because smorest/Marshmallow does that for us based on the schema
            # then SQLAlchemy turns it into the correct format for the db based on the model
            current_app.logger.debug(f"Job data to store to db : {job}")

            db.session.add(job)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred when inserting to db")
        except Exception as e:
            db.session.rollback()
            abort(500, message=str(e))

        return job

###################################################################################################
#  End of File
###################################################################################################
