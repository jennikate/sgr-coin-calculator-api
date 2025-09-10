"""
Test configuration.
"""

###################################################################################################
# Imports
###################################################################################################

import logging
import os
import sys
import pytest

from alembic import command
from alembic.config import Config
from sqlalchemy_utils import drop_database, create_database # type: ignore
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import inspect

from src import create_app, db as _db
from src.api.models import RankModel # type: ignore


###################################################################################################
# Configuration & setup
###################################################################################################
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MIGRATIONS_DIR = os.path.join(BASE_DIR, "migrations")

@pytest.fixture
def db():
    """Expose the SQLAlchemy db object for tests."""
    return _db

@pytest.fixture(scope="session")
def app():
    """Create Flask app in testing config and push context."""
    app = create_app("testing")
    ctx = app.app_context()
    ctx.push()
    return app


@pytest.fixture(scope="session", autouse=True)
def apply_migrations(app):
    """Drop & recreate the test DB, then run migrations fresh."""

    app.logger.info("---------- apply_migrations fixture ----------")

    uri = app.config["SQLALCHEMY_DATABASE_URI"]
    app.logger.debug(f"Recreating test DB at {uri}")

    # Drop + create ensures we never depend on downgrade()
    drop_database(uri)
    create_database(uri)

    # Configure Alembic
    alembic_cfg = Config(os.path.join(MIGRATIONS_DIR, "alembic.ini"))
    alembic_cfg.set_main_option("script_location", MIGRATIONS_DIR)
    alembic_cfg.set_main_option("sqlalchemy.url", uri)

    # Apply all migrations
    command.upgrade(alembic_cfg, "head")

    # Verify important tables exist
    inspector = inspect(_db.engine)
    tables = inspector.get_table_names()
    app.logger.debug(f"Tables after migration: {tables}")

    if "ranks" not in tables:
        raise RuntimeError("Migration did not create 'ranks' table")

    yield

    # optional cleanup: drop DB after test session
    # drop_database(uri)


@pytest.fixture(scope="function", autouse=True)
def session(app):
    """Run each test in its own transaction (rollback after)."""
    connection = _db.engine.connect()
    transaction = connection.begin()

    SessionFactory = sessionmaker(bind=connection, expire_on_commit=False)
    session = scoped_session(SessionFactory)

    _db.session = session

    yield session

    transaction.rollback()
    connection.close()
    session.remove()


###################################################################################################
# Seeds
###################################################################################################

@pytest.fixture
def sample_ranks(db):
    ranks = [
        RankModel(name="Captain", position=1, share=1.0),
        RankModel(name="Lieutenant", position=2, share=1.0),
        RankModel(name="Blagguard", position=3, share=0.75),
    ]
    db.session.add_all(ranks)
    db.session.commit()
    return ranks

@pytest.fixture
def sample_members(db, sample_ranks):
    from src.api.models import MemberModel # type: ignore
    members = [
        MemberModel(name="Bob", rank_id=sample_ranks[0].id),
        MemberModel(name="Charlie", rank_id=sample_ranks[1].id),
        MemberModel(name="Alice", rank_id=sample_ranks[2].id),
    ]
    db.session.add_all(members)
    db.session.commit()
    return members
