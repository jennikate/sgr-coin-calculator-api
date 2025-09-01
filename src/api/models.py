# type: ignore
# disable type checking on file as SQLAlchmey isn't playing nice with MyPy
"""
SQLAlchemy models for the API.
"""

###################################################################################################
#  Imports
###################################################################################################

from uuid import uuid4

from src import db

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

    id = db.Column(Uuid(), primary_key=True, default=uuid4)
    name = db.Column(db.String(20), unique=True, nullable=False)
    position = db.Column(db.Integer, unique=True, nullable=False)
    share = db.Column(db.Float(precision=2), nullable=False)

    def __repr__(self):
        return f"<Rank: {self.name} at position {self.position} with share {self.share}>"
    

    
###################################################################################################
# End of file
###################################################################################################

