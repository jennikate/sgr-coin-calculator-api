"""
Config for tests.
"""

###################################################################################################
# Imports
###################################################################################################

import datetime
import os
import pytest

from alembic import command
from alembic.config import Config
from sqlalchemy_utils import drop_database, create_database # type: ignore
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import inspect

from constants import DEFAULT_RANK # type: ignore
from src import create_app, db as _db
from src.api.models import JobModel, MemberModel, RankModel # type: ignore


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
    # note the default rank should have been added as part of your migrations
    # see docs/creation-notes.md#Creating and updating the db if you are getting
    # errors due to missing default rank
    ranks = [
        RankModel(name="Captain", position=1, share=1.0),
        RankModel(name="Lieutenant", position=2, share=1.0),
        RankModel(name="Blagguard", position=3, share=0.75),
        RankModel(name="Runt", position=4, share=0.5),
    ]
    db.session.add_all(ranks)
    db.session.commit()
    return ranks


@pytest.fixture
def sample_members(db, sample_ranks):
    members = [
        MemberModel(name="Bob", rank_id=sample_ranks[0].id),
        MemberModel(name="Charlie", rank_id=sample_ranks[1].id),
        MemberModel(name="Sue", rank_id=sample_ranks[2].id),
        MemberModel(name="Alice", rank_id=sample_ranks[2].id),
        MemberModel(name="JoeDefault", rank_id=DEFAULT_RANK["id"]),
    ]
    db.session.add_all(members)
    db.session.commit()
    return members

@pytest.fixture
def sample_jobs(db):
    # These are the combinations for POSTing a new job, before members are added or payouts calculated
    jobs = [
        JobModel(
            job_name="Ogres in Hinterlands",
            job_description="For Stromgarde, collecting horns for bounty",
            start_date=datetime.date.fromisoformat("2025-04-23"), # have to format these in the postgres required way for fixture creation
            end_date=datetime.date.fromisoformat("2025-04-28"),
            total_silver=100
        ),
        JobModel(
            job_name="Grace artifact",
            job_description="EPL highborne staff",
            start_date=datetime.date.fromisoformat("2025-04-29"),
            total_silver=1500
        ),
        JobModel(
            job_name="Adhoc troll tusks",
            start_date=datetime.date.fromisoformat("2025-05-03")
        )
    ]
    db.session.add_all(jobs)
    db.session.commit()
    return jobs


@pytest.fixture
def job_with_members(client, sample_jobs, sample_members):
    """
    Creates a job and adds members to it.
    Returns the job id and the members added for use in tests.
    """
    # Take the first job from the sample_jobs fixture
    job = sample_jobs[0]
    job_id = job.id

    # Take some members from sample_members
    # members_to_add = [str(m.id) for m in sample_members[:3]]
    members_to_add = [
        str(sample_members[0].id),
        str(sample_members[1].id),
        str(sample_members[2].id)
    ]

    # Update the job to add members
    update_payload = {"add_members": members_to_add}
    response = client.patch(f"/v1/job/{job_id}", json=update_payload)
    
    # Ensure the update succeeded
    assert response.status_code == 200

    # Return both the job id and the members added
    return {
        "job_id": job_id,
        "members": sample_members[:3],
        "job": job
    }


###################################################################################################
#  END OF FILE
###################################################################################################
