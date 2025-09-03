"""
Test configuration.
"""

###################################################################################################
# Imports
###################################################################################################

import pytest

from src import create_app
from src.extensions import db as _db
from sqlalchemy_utils import create_database, drop_database # type: ignore
from sqlalchemy import create_engine


###################################################################################################
# Fixtures
###################################################################################################

@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    yield app


@pytest.fixture(scope="session")
def db(app):
    with app.app_context():
        _db.drop_all()
        _db.create_all()
        yield _db
        _db.drop_all()
    

@pytest.fixture(scope="function")
def client(app, db):
    with app.test_client() as client:
        yield client
