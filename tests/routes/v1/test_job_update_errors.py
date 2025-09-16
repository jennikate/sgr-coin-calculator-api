"""
This module contains a unit test for the job & job endpoint resource in the `src.api.v1/job_routes` module.
"""

## TODO: refactor tests to remove hardcoded values where possible
## TODO: refactor tests to use fixtures where possible
## TODO: review if util functions can be used to reduce code duplication

###################################################################################################
#  IMPORTS
###################################################################################################

from uuid import uuid4
import pytest

from sqlalchemy.exc import SQLAlchemyError

from src.extensions import db
from tests.test_helpers import assert_job_update


###################################################################################################
#  ERRORS
###################################################################################################

@pytest.mark.usefixtures("sample_jobs")
class TestUpdateJobErrors:
    def test_update_job_that_doesnt_exist(self, client, sample_jobs):
        updated_job = {
            "job_name": "New jobs",
            "start_date": '2025-01-01',
        }
        response = client.patch(f"/v1/job/99", json=updated_job)
        assert response.status_code == 400
        assert response.get_json() ==  {
            "code": 400,
            "message": "Invalid job id",
            "status": "Bad Request"
        }


    def test_update_job_invalid_values(self, client, sample_jobs):
        """
        Tests that it errors if the fields are invalid
        """
        # Get an id to update
        id = sample_jobs[0].id 
        # Create the update details
        updated_job = {
            "job_name": "Too long a string for this field. Too long a string for this field. Too long a string for this field. Too long a string for this field. ",
            "job_description": "Too long a string for this field. Too long a string for this field. Too long a string for this field. Too long a string for this field. Too long a string for this field. Too long a string for this field. Too long a string for this field. Too long a string for this field. Too long a string for this field. Too long a string for this field. ",
            "start_date": "0101",
            "end_date": "01-01-2025",
            "total_silver": -100.00
        }

        # verify details of the original job are different to the update job
        original_response = client.get(f"/v1/job/{id}")
        assert original_response != updated_job

        # update the job
        update_response = client.patch(f"/v1/job/{id}", json=updated_job)
        updated_expected_response = {
            "code": 422,
            "errors": {
                "json": {
                    "end_date": [
                        "Not a valid date."
                    ],
                    "job_description": [
                        "job_description must not exceed 256 characters."
                    ],
                    "job_name": [
                        "job_name must not exceed 100 characters."
                    ],
                    "start_date": [
                        "Not a valid date."
                    ],
                    "total_silver": [
                        "total_silver cannot be a negative value."
                    ]
                }
            },
            "status": "Unprocessable Entity"
        }
        assert update_response.status_code == 422
        assert update_response.get_json() == updated_expected_response


    def test_update_job_sqlalchemy_error(self, client, sample_jobs, monkeypatch):
        """
        Tests that a 500 response with a message is returned if the PATCH raises a SQLAlchemyError.
        """
        id = sample_jobs[0].id 
        # Monkeypatch db.session.commit to raise SQLAlchemyError
        def bad_commit():
            raise SQLAlchemyError("DB error")

        monkeypatch.setattr(db.session, "commit", bad_commit)

        updated_job = {
            "job_name": "job Name",
            "start_date": "2025-01-01",
        }
        response = client.patch(f"/v1/job/{id}", json=updated_job)

        assert response.status_code == 500
        data = response.get_json()
        assert "An error occurred when inserting to db" in data["message"]


    def test_update_job_generic_error(self, client, sample_jobs, monkeypatch):
        """
        Tests that a 500 response with a message is returned if the PATCH raises any other error.
        """
        id = sample_jobs[0].id 

        def bad_commit():
            raise RuntimeError("Something went wrong!")

        monkeypatch.setattr(db.session, "commit", bad_commit)

        updated_job = {
            "job_name": "job Name",
            "start_date": "2025-01-01",
        }
        response = client.patch(f"/v1/job/{id}", json=updated_job)
        assert response.status_code == 500
        data = response.get_json()
        assert "Something went wrong!" in data["message"] 


    # Testing model/schema validation
    def test_update_members_with_bad_uuid(self, client, sample_members, sample_jobs):
        """
        Tests that a user can update a job in the API.
        """
        # Get an id to update
        job_id = sample_jobs[0].id 
        
        updated_job = {
            "total_silver": 83,
            "add_members": [str(sample_members[0].id), "baduuid", str(sample_members[1].id)]
        }

        expected_response = {
            "code": 422,
            "errors": {
                "json": {
                    "add_members": {
                        "1": [
                            "Not a valid UUID."
                        ]
                    }
                }
            },
            "status": "Unprocessable Entity"
        }
        
        # Call the reusable helper
        assert_job_update(
            client=client,
            job_id=job_id,
            updated_job=updated_job,
            expected_response=expected_response,
            expected_status=422
        )

        
###################################################################################################
#  End of file.
###################################################################################################
