"""
This module contains test for /payments endpoint from the `src.api.v1/job_routes` module.
"""

###################################################################################################
#  IMPORTS
###################################################################################################

import pytest

from sqlalchemy.exc import SQLAlchemyError
from uuid import uuid4

from src.extensions import db


###################################################################################################
#  ERROR CASES
###################################################################################################

@pytest.mark.usefixtures("job_with_members")
class TestGetPaymentsErrors:
    def test_get_payement_invalid_uuid(self, client):
        """
        Errors if the uuid is malformed
        """

        response = client.get(f"/v1/job/notauuid/payments")
        assert response.status_code == 400
        assert response.get_json() == {
            "code": 400,
            "message": "Invalid job id",
            "status": "Bad Request"
        }

    def test_get_payement_no_job_for_uuid(self, client):
        """
        Errors if the uuid is valid but there's no job for it
        """

        response = client.get(f"/v1/job/{uuid4()}/payments")
        assert response.status_code == 404
        assert response.get_json() == {
            "code": 404,
            "status": "Not Found"
        }

    def test_update_job_sqlalchemy_error(self, client, job_with_members, monkeypatch):
        """
        Tests that a 500 response with a message is returned if the PATCH raises a SQLAlchemyError.
        """
        job_id = job_with_members["job_id"]

        # Monkeypatch db.session.commit to raise SQLAlchemyError
        def bad_commit():
            raise SQLAlchemyError("DB error")

        monkeypatch.setattr(db.session, "commit", bad_commit)

        response = client.get(f"/v1/job/{job_id}/payments")

        assert response.status_code == 500
        data = response.get_json()
        assert "An error occurred when inserting to db" in data["message"]


    def test_update_job_generic_error(self, client, job_with_members, monkeypatch):
        """
        Tests that a 500 response with a message is returned if the PATCH raises any other error.
        """
        job_id = job_with_members["job_id"]

        def bad_commit():
            raise RuntimeError("Something went wrong!")

        monkeypatch.setattr(db.session, "commit", bad_commit)

        response = client.get(f"/v1/job/{job_id}/payments")
        assert response.status_code == 500
        data = response.get_json()
        assert "Something went wrong!" in data["message"] 


###################################################################################################
#  End of file.
###################################################################################################
