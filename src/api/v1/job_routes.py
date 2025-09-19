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

from constants import COMPANY_CUT, DEFAULT_RANK # type: ignore
from datetime import date, datetime
from decimal import Decimal, ROUND_DOWN
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
        # Flask-Smorest automatically deserializes the incoming request JSON into this schema 
        # (because you annotate your route with @blp.arguments(MemberUpdateSchema)).
        # Marshmallow tries to coerce fields -> e.g. member_id into a uuid.UUID object.
        # If the string is not a valid UUID it raises a ValidationError.
        # Flask-Smorest catches that and returns a 422 with the error details.
        current_app.logger.debug("---------------- STARTING PATCH --------------")
        try:
            job_uuid = UUID(job_id)  # converts string to UUID object
        except ValueError:
            abort(400, message="Invalid job id")

        # Eager-load members_on_job and associated members
        job = JobModel.query.options(
            joinedload(JobModel.members_on_job).joinedload(MemberJobModel.member)
        ).get_or_404(job_uuid)

        ## ORDERING
        # Bad UUIDs or other value formats are checked by Marshmallow/smorest as part of deserialization
        # based on what we defined in model/schemas.
        # so error out before code reaches here.

        # We define some variables that will let us know if we need to reset payment
        # and that its safe to run the update
        # Having this check before updating lets us ensure nothing on the job is updated
        # when we return an error
        # And lets us ensure the payments are reset regardless of when the session is updated
        # e.g. job.total_silver in session will get updated to the updated_data.total_silver value
        # if we didn't have this counter/check and the job.total_silver updated in session before
        # we ran the reset payment? check it may get missed because job.total_silver would equal updated_data.total_silver
        total_members_to_add = 0
        total_members_to_remove = 0
        total_silver_different = "total_silver" in update_data and job.total_silver != update_data["total_silver"]
        total_job_changes = 0

        # Add members
        if "add_members" in update_data:
            for member_id in update_data.get("add_members", []):
                member_uuid = UUID(str(member_id))

                # check if already exists on MemberJob table and ignore if it does
                if not any(jm.member_id == member_id for jm in job.members_on_job):
                    # if doesn't exist yet get the member model
                    member = MemberModel.query.get(member_uuid)
                    # if we find a member and it has a default rank do not add it & prompt user to update rank first
                    # otherwise append it
                    if member:
                        if member.rank.id == DEFAULT_RANK["id"]:
                            abort(400, message=f"At least one member {member.name} ({member.id}) has DEFAULT rank, you must update them before adding to a job")
                        else:
                            job.members_on_job.append(
                                MemberJobModel(
                                    member_id=member.id,
                                    job_id=job.id,
                                    member_rank=member.rank.name,
                                )
                            )
                            # update our counter so we know how many members were added
                            total_members_to_add += 1
                    else:
                        # error out if they're trying to add a member that doesn't exist
                        abort(404, message=f"Member {member_uuid} not found")

        # Remove members
        if "remove_members" in update_data:
            for member_id in update_data.get("remove_members", []):
                member_uuid = UUID(str(member_id))

                # Check member is on the association object
                job_member = db.session.query(MemberJobModel).filter_by(
                    job_id=job.id,
                    member_id=member_uuid
                ).first()

                if job_member:
                    db.session.delete(job_member) # remove from session but not yet from db
                    total_members_to_remove += 1
        
        # Update job details 
        job_fields = {field.name for field in JobModel.__table__.columns if field.name != "id"}
        for key, value in update_data.items():
            if key in job_fields:
                setattr(job, key, value)
                total_job_changes += 1

        # Reset payments
        if total_members_to_add > 0 or total_members_to_remove > 0 or total_silver_different:
            current_app.logger.info("------- RESETTING PAYMENT DATA ------")
            job.company_cut_amt = None
            job.remainder_after_payouts = None
            for jm in job.members_on_job:
                jm.member_pay = None
        
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
            db.session.refresh(job)
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


# TODO: refactor this to make less repetitive esp around validating we have all required details
@blp.route("/job/<job_id>/payments")
class JobWithPaymentsById(MethodView):
    """
    Resources for getting a job with its payments.
    """
    @blp.response(200, JobResponseSchema)
    def get(self, job_id):
        """
        Get job by id and calculate its payment amounts
        """
        try:
            job_uuid = UUID(job_id)  # checks it is a valid UUID format & rejects early
        except ValueError:
            abort(400, message=f"Invalid job -> {job_id}")

        # Eager-load members_on_job, member, and rank
        job = JobModel.query.options(
            joinedload(JobModel.members_on_job)
            .joinedload(MemberJobModel.member)
            .joinedload(MemberModel.rank)
        ).get_or_404(job_uuid)

        if not job.members_on_job:
            abort(400, message="Job has no members, you must PATCH some to the job before requesting payment")

        current_app.logger.debug("--------- CALCULATING TOTALS ----------")

        company_cut = job.total_silver * COMPANY_CUT
        payable_to_members = job.total_silver - company_cut
        current_app.logger.debug(f"Company cut -> payable_to_members [{payable_to_members}] = job.total_silver [{job.total_silver}] - (job.total_silver [{job.total_silver}] * company_cut [{COMPANY_CUT}]")

        total_shares = sum(jm.member.rank.share for jm in job.members_on_job if jm.member and jm.member.rank)
        current_app.logger.debug(f"Total shares -> {total_shares}")
        
        value_per_share = payable_to_members / total_shares
        current_app.logger.debug(f"Value per share [{value_per_share}] -> payable_to_members [{payable_to_members}] / total_shares [{total_shares}]")

        total_paid = 0 # starts at 0

        # Dynamically calculate pay for each member-job
        for jm in job.members_on_job:
            jm.member_pay = self.calculate_member_pay(jm.member, value_per_share)
            current_app.logger.debug(f"Paid to {jm.member.name} -> {jm.member_pay}")
            current_app.logger.debug(f"value type is {type(jm.member_pay)}")
            total_paid += jm.member_pay
        current_app.logger.debug(f"Total Paid -> {total_paid}")
        
        # Commit the job.company_cut, job.remainder_after_payouts, and member.member_pay to the database
        try:
            job.company_cut_amt = company_cut
            job.remainder_after_payouts = job.total_silver - company_cut - total_paid
            db.session.commit()
        except SQLAlchemyError as sqle:
            current_app.logger.debug(f"500 SQLAlchemyError -> {sqle}")
            db.session.rollback()
            abort(500, message="An error occurred when inserting to db")
        except Exception as e:
            current_app.logger.debug(f"500 Exception -> {e}")
            db.session.rollback()
            abort(500, message=str(e))

        return job
    
    @staticmethod
    def calculate_member_pay(member, value_per_share):
        """
        Calculate a member's pay based on their rank's share.
        """
        current_app.logger.debug("--------- CALCULATING PAY FOR MEMBER ----------")
        current_app.logger.debug(f"Member -> {getattr(member, "name", None)} with {getattr(getattr(member, "rank", None), "share", None)} shares")
        if not member or not member.rank or not member.rank.share:
            current_app.logger.debug(f"member or member.rank.share not found")
            return 0.0
        
        member_share = member.rank.share
        raw_value = Decimal(member_share * value_per_share)
        return int(raw_value.to_integral_value(rounding=ROUND_DOWN))  # <-- ensures 0 decimals, as we pay only silver not silver copper


###################################################################################################
#  End of File
###################################################################################################
