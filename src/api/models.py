# type: ignore
# disable type checking on file as SQLAlchmey isn't playing nice with MyPy
"""
SQLAlchemy models for the API.
"""

###################################################################################################
#  Imports
###################################################################################################

# from uuid import uuid4

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

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    position = db.Column(db.Integer, unique=True, nullable=False)
    share = db.Column(db.Float(precision=2), nullable=False)

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id}, name={self.name!r}, position={self.position}, share={self.share})>"
    

    
###################################################################################################
# End of file
###################################################################################################

