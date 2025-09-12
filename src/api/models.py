# type: ignore
# disable type checking on file as SQLAlchmey isn't playing nice with MyPy
"""
SQLAlchemy models for the API.
"""

###################################################################################################
#  Imports
###################################################################################################

from datetime import date
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID as pgUUID # type: ignore

from src.extensions import db

###################################################################################################
# Classes
###################################################################################################

class MemberJobModel(db.Model):
    """
    SQLAlchemy model for a ranks table.

    :member_id: From the Member table.
    :job_id: From the Job table.
    :member_rank: Copied from the Member table to preserve history.
    :member_pay: Calculated and patched in when user runs the 'calculate pay' endpoint (not yet written)
    """
    __tablename__ = 'member_job'
    member_id = db.Column(db.UUID, db.ForeignKey('members.id'), primary_key=True)
    job_id = db.Column(db.UUID, db.ForeignKey('job.id'), primary_key=True)

    member_rank = db.Column(db.String, nullable=False)
    member_pay = db.Column(db.Float, nullable=False)

    member = db.relationship("MemberModel", back_populates="member_jobs")
    job = db.relationship("JobModel", back_populates="member_jobs")


class RankModel(db.Model):
    """
    SQLAlchemy model for a ranks table.

    :position: A manually determined position for the rank, it must be unique.
    :share: The number of shares (in x.xx format) that rank receives from the total pay.
    """
    __tablename__ = 'ranks'

    id = db.Column(
        pgUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        unique=True,
        nullable=False
    )
    name = db.Column(db.String(20), unique=True, nullable=False)
    position = db.Column(db.Integer, unique=True, nullable=False)
    share = db.Column(db.Float(precision=2), nullable=False)

    members = db.relationship('MemberModel', back_populates='rank')
    # could do cascade='all, delete-orphan which would delete all associated members if a rank is deleted
    # but I don't want to lose the members so this isn't useful here
    # instead we have `ondelete='SET NULL'`` in the MemberModel and we update it to a DEFAULT_VALUE
    # when we delete the rank
    # members = db.relationship('Member', back_populates='rank', cascade='all, delete-orphan')

    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id}, name={self.name!r}, position={self.position}, share={self.share})>"
    

class MemberModel(db.Model):
    """
    SQLAlchemy model for a members table.

    :name: The character name to use as a reference - ideally full name.
    :rank: The character rank, relation from the RankModel.
    """
        
    __tablename__ = 'members'

    id = db.Column(
        pgUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        unique=True,
        nullable=False
    )
    name = db.Column(db.String(256), unique=True, nullable=False)
    status = db.Column(db.Boolean, default=True, nullable=False) # active/inactive status

    # foreign key to ranks table
    # There is no ondelete as in the RankResources for delete we update all children (members)
    # who have that rank, before we delete the rank
    rank_id = db.Column(db.UUID, db.ForeignKey('ranks.id'), nullable=False)

    # relationship for easy access
    rank = db.relationship('RankModel', back_populates='members')
    # relationship to association object
    member_jobs = db.relationship("MemberJobModel", back_populates="member")
    jobs = db.relationship("JobModel", secondary="member_job", back_populates="members", viewonly=True)
    # The viewonly=True in the secondary relationship is optional but helps prevent accidental inserts directly through the secondary link.
    # You can still query member.jobs to see all jobs for a member.
    # But if you try to append or remove items, SQLAlchemy will prevent it, avoiding accidental inserts that would be missing required data like member_rank and member_pay.

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id}, name={self.name!r}, rank={self.rank})>"
        # !r means apply the repr() function to the value. Effectively it's apply '' to follow the repr formatting

class JobModel(db.Model):
    """
    SQLAlchemy model for a jobs table.
    """
    __tablename__ = 'job'
    id = db.Column(
        pgUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        unique=True,
        nullable=False
    )
    job_name = db.Column(db.String(100), nullable=False)
    job_description = db.Column(db.String(256))
    start_date = db.Column(db.Date, default=date.today, nullable=False) 
    end_date = db.Column(db.Date)
    total_silver = db.Column(db.Integer)
    company_cut_amt = db.Column(db.Float)
    remainder_after_payouts = db.Column(db.Float)
    
    # relationship to association object
    member_jobs = db.relationship("MemberJobModel", back_populates="job")
    members = db.relationship("MemberModel", secondary="member_job", back_populates="jobs", viewonly=True)

    # def __repr__(self):
    #     return f"""<{self.__class__.__name__}(
    #         id={self.id}, 
    #         job_name={self.job_name!r}
    #         job_description={self.job_description!r}
    #         start_date={self.start_date!r}
    #         end_date={self.end_date!r}
    #         total_silver={self.total_silver}
    #         company_cut_amount={self.company_cut_amount}
    #         remainder_after_payouts={self.remainder_after_payouts}
    #     )>
    #     """
    
###################################################################################################
# End of file
###################################################################################################
