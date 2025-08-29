# type: ignore
# disable type checking on file as SQLAlchmey isn't playing nice with MyPy
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class RankModel(db.Model):
    __tablename__ = 'ranks'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    position = db.Column(db.Integer, unique=True, nullable=False)
    share = db.Column(db.Float(precision=2), nullable=False)