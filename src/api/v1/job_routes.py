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

from datetime import date, datetime
from flask import current_app
from flask.views import MethodView
from flask_smorest import Blueprint, abort # type: ignore
from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError # to catch db errors
from sqlalchemy.orm import joinedload
from uuid import UUID

from src.api.models import JobModel, MemberJobModel, MemberModel, RankModel # type: ignore
from src.api.schemas import JobQueryArgsSchema, BaseJobSchema, JobResponseSchema, JobUpdateSchema, MemberJobResponseSchema, MemberSchema, MessageSchema

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
    @blp.arguments(BaseJobSchema)
    @blp.response(201, BaseJobSchema)
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


@blp.route("/jobs")
class AllJobsResource(MethodView):
    """
    Resource for getting all jobs.
    """
    @blp.arguments(JobQueryArgsSchema, location="query")
    @blp.response(200, JobResponseSchema(many=True))
    def get(self, args):
        """
        Get all Jobs
        """
        current_app.logger.debug(f"Getting jobs with args: {args}")
        query = JobModel.query

        # Apply filter if exists
        date = args.get("start_date")  # Matches the schema field name
        if date is not None:
            query = query.filter(JobModel.start_date == date)

        # Apply sorting
        jobs = query.order_by(JobModel.start_date.desc()).all()

        return jobs
    

@blp.route("/job/<job_id>")
class JobByIdResource(MethodView):
    """
    Resources for getting, updating or deleting a job by id.
    """
    @blp.response(200, JobResponseSchema)
    def get(self, job_id):
        """
        Get job by id
        """
        try:
            data = UUID(job_id)  # converts string to UUID object
        except ValueError:
            abort(400, message="Invalid job id")

        job = JobModel.query.get_or_404(data)
        return job
    
    @blp.arguments(JobUpdateSchema(partial=True)) # allow partial updates
    @blp.response(200, JobResponseSchema)
    def patch(self, update_data, job_id):
        """
        Update job partially by id, including adding and removing members.
        """
        try:
            job_uuid = UUID(job_id)  # converts string to UUID object
        except ValueError:
            abort(400, message="Invalid job id")

        # Eager-load members_on_jobs and associated members
        job = JobModel.query.options(
            joinedload(JobModel.members_on_jobs).joinedload(MemberJobModel.member)
        ).get_or_404(job_uuid)

        # Update job details
        # TODO: update other resources to use this pattern
        job_fields = {field.name for field in JobModel.__table__.columns if field.name != "id"}
        for key, value in update_data.items():
            if key in job_fields:
                setattr(job, key, value)

        # Add / Update members
        if "add_members" in update_data:
            for member_id in update_data.get("add_members", []):
                try:
                    current_app.logger.debug("---------------- TRY ADD MEMBERS --------------")
                    current_app.logger.debug(f"member uuid checking {str(member_id)}")
                    member_uuid = UUID(str(member_id))
                except ValueError:
                    abort(400, message=f"Invalid member_id format: {member_id}")

                member = MemberModel.query.get(member_uuid)
                if not member:
                    abort(404, message=f"Member {member_uuid} not found")

                # Check if association already exists
                job_member = next(
                    (jm for jm in job.members_on_jobs if jm.member_id == member.id),
                    None
                )

                # Create new association
                if not job_member:
                    job_member = MemberJobModel(
                        job=job,
                        member=member,
                        member_rank=member.rank.name,  # copy from Member at creation
                    )

                    job.members_on_jobs.append(job_member)

        # Remove members
        if "remove_members" in update_data:
            current_app.logger.debug("---------------- TRY REMOVE MEMBERS --------------")
            current_app.logger.debug(f"removing members: {(update_data["remove_members"])}")
            current_app.logger.debug(f"remove_members is of length {len(update_data["remove_members"])}")
            for member_id in update_data.get("remove_members", []):
                try:
                    member_uuid = UUID(str(member_id))
                except ValueError:
                    abort(400, message=f"Invalid member_id format: {member_uuid}")

                # Check member is on the association object
                job_member = next(
                    (jm for jm in job.members_on_jobs if jm.member_id == member_uuid),
                    None
                )
                if job_member:
                    db.session.delete(job_member)

        try:
            # NOTE:
            # when we did something like job = Job.query.get_or_404(job_uuid)
            # SQLAlchemy automatically loads job into the current session.
            # Any changes you make to its attributes (e.g., job.job_name = "New Name") are tracked by the session.
            # so at db.session.commit()
            # SQLAlchemy flushes all changes for any objects in the session, including job and any JobMember rows you appended/modified.
            # db.session.add(job) isn’t required — it’s already known to the session.
            # TODO: review other code and check if db.session.add() is needed
            db.session.commit()
        except SQLAlchemyError as sqle:
            db.session.rollback()
            import traceback
            print(traceback.format_exc())
            current_app.logger.debug(f"500 error with {str(sqle)}")
            abort(500, message="An error occurred when inserting to db")
        except Exception as e:
            db.session.rollback()
            abort(500, message=str(e))
        
        return job

    @blp.response(200, MessageSchema)
    def delete(self, job_id):
        """
        Delete job by id
        """
        try:
            data = UUID(job_id)  # converts string to UUID object
        except ValueError:
            abort(400, message="Invalid job id")

        job = JobModel.query.get_or_404(data)

        try:
            db.session.delete(job)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred when inserting to db")
        except Exception as e:
            db.session.rollback()
            abort(500, message=str(e))

        return { "message": f"job id {job_id} deleted" }, 200


@blp.route("/job/<uuid:job_id>/payments")
@blp.response(200, MemberJobResponseSchema(many=True))
def get_payments(job_id):
    job = JobModel.query.options(
        joinedload(JobModel.members_on_jobs).joinedload(MemberJobModel.member)
    ).get_or_404(job_id)

    # Calculate payments and attach to model instances
    for jm in job.members_on_jobs:
        jm.calculated_pay = 1.00  # replace with real calculation

    return MemberJobResponseSchema(many=True).dump(job.members_on_jobs)


###################################################################################################
#  End of File
###################################################################################################
