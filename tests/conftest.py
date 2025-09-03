"""
Test configuration.
"""

###################################################################################################
# Imports
###################################################################################################

import pytest

from sqlalchemy import text
from src import create_app, db as _db


###################################################################################################
# Fixtures
###################################################################################################

@pytest.fixture(scope="session")
def app():
    """Create and configure a new app instance for tests."""
    app = create_app("testing")
    with app.app_context():
        yield app


@pytest.fixture(scope="session")
def db(app):
    schema_name = "test_schema"

    engine = _db.engine
    with engine.connect() as conn:
        conn.execute(text(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE;"))
        conn.execute(text(f"CREATE SCHEMA {schema_name};"))
        conn.execute(text(f"SET search_path TO {schema_name};"))

    _db.metadata.schema = schema_name
    with app.app_context():
        _db.drop_all() # drop old tables to ensure clean state
        _db.create_all() # create all tables from your models
        yield _db
        _db.drop_all()

    with engine.connect() as conn:
        conn.execute(text(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE;"))
    
