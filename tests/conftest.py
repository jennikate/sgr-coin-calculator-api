"""
Global pytest fixtures for tests.
"""

###################################################################################################
#  Imports
###################################################################################################

import os
import pytest
import psycopg2 # type: ignore
from psycopg2 import OperationalError
import time

from sqlalchemy import event
from sqlalchemy.engine import Engine

from src import create_app
from src.extensions import db


###################################################################################################
# Utils
###################################################################################################
print("DB URI:", os.getenv("DATABASE_URL"))

def wait_for_postgres(host="localhost", port=5544, user="test_user", password="test_password", db="myapp_test", timeout=30):
    start = time.time()
    while True:
        try:
            conn = psycopg2.connect(
                host=host, port=port, user=user, password=password, dbname=db
            )
            conn.close()
            return
        except OperationalError:
            if time.time() - start > timeout:
                raise
            time.sleep(1)


###################################################################################################
# Fixtures
###################################################################################################

@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    print(">>> USING DB:", app.config["SQLALCHEMY_DATABASE_URI"])  # 👈 confirm here

    with app.app_context():
        wait_for_postgres()
        db.drop_all()
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


@pytest.fixture(scope="function")
def session(app):
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)
    db.session = session

    yield session

    transaction.rollback()
    connection.close()
    session.remove()
