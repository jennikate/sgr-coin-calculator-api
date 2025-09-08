# type: ignore
# disable type checking on file as SQLAlchmey isn't playing nice with MyPy
"""
SQLAlchemy models for the API.
"""

###################################################################################################
#  Imports
###################################################################################################

from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID as pgUUID # type: ignore

from src.extensions import db

###################################################################################################
# Classes
###################################################################################################

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
    rank_id = db.Column(db.UUID, db.ForeignKey('ranks.id'), nullable=False)

    # relationship for easy access
    rank = db.relationship('RankModel', back_populates='members')


    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id}, name={self.name!r}, rank={self.rank})>"
    

###################################################################################################
# End of file
###################################################################################################

