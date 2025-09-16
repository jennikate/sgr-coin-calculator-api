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


###################################################################################################
#  ERRORS
###################################################################################################


class TestPostJobErrors:
    def test_post_job_no_payload(self, client):
        """
        Tests that a job is rejected if there is no payload.
        """
        new_job = {}
        response = client.post("/v1/job", json=new_job)
        data = response.get_json()

        expected_response = {
            "code": 422,
            "errors": {
                "json": {
                    "job_name": [
                        "Missing data for required field."
                    ],
                    "start_date": [
                        "Missing data for required field."
                    ],
                }
            },
            "status": "Unprocessable Entity"
        }

        assert response.status_code == 422
        assert data == expected_response

    
    def test_post_job_empty_strings(self, client):
        """
        Tests that a job is rejected if required strings exist but are empty.
        """
        new_job = {
            "job_name": "",
            "start_date": ""
        }
        response = client.post("/v1/job", json=new_job)
        data = response.get_json()

        expected_response = {
            "code": 422,
            "errors": {
                "json": {
                    "job_name": [
                        "job_name must not be empty."
                    ],
                    "start_date": [
                        "Not a valid date."
                    ]
                }
            },
            "status": "Unprocessable Entity"
        }

        assert response.status_code == 422
        assert data == expected_response


    def test_post_job_missing_required_keys(self, client):
        """
        Tests that a job is rejected if required fields are missing
        """
        new_job = {
            "job_description": "For Stromgarde, collecting horns for bounty",
            "end_date": "2025-04-28",
            "total_silver": 100
        }
        response = client.post("/v1/job", json=new_job)
        data = response.get_json()

        expected_response = {
            "code": 422,
            "errors": {
                "json": {
                    "job_name": [
                        "Missing data for required field."
                    ],
                    "start_date": [
                        "Missing data for required field."
                    ],
                }
            },
            "status": "Unprocessable Entity"
        }

        assert response.status_code == 422
        assert data == expected_response


    def test_post_job_invalid_formats(self, client):
        """
        Tests that a job is rejected if the format for fields is invalid
        """
        new_job = {
            "job_name": 7,
            "job_description": 7,
            "start_date": "01072025",
            "end_date": "28/4/2025",
            "total_silver": "abc"
        }
        response = client.post("/v1/job", json=new_job)
        data = response.get_json()

        expected_response = {
            "code": 422,
            "errors": {
                "json": {
                    "end_date": [
                        "Not a valid date."
                    ],
                    "job_description": [
                        "Not a valid string."
                    ],
                    "job_name": [
                        "Not a valid string."
                    ],
                    "start_date": [
                        "Not a valid date."
                    ],
                    "total_silver": [
                        "Value must be a whole number."
                    ],
                }
            },
            "status": "Unprocessable Entity"
        }

        assert response.status_code == 422
        assert data == expected_response


    def test_post_job_invalid_values(self, client):
        """
        Tests that a job is rejected if the length of fields is invalid
        """
        new_job = {
            "job_name": "Too long a string for this field. Too long a string for this field. Too long a string for this field. Too long a string for this field. ",
            "job_description": "Too long a string for this field. Too long a string for this field. Too long a string for this field. Too long a string for this field. Too long a string for this field. Too long a string for this field. Too long a string for this field. Too long a string for this field. Too long a string for this field. Too long a string for this field. ",
            "start_date": "0101",
            "end_date": "01-01-2025",
            "total_silver": -100.00
        }
        response = client.post("/v1/job", json=new_job)
        data = response.get_json()

        expected_response = {
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

        assert response.status_code == 422
        assert data == expected_response


    def test_post_job_invalid_number(self, client):
        """
        Tests that a job is rejected if the length of fields is invalid
        """
        new_job = {
            "job_name": "Ogres in Hinterlands",
            "job_description": "For Stromgarde, collecting horns for bounty",
            "start_date": "2025-04-23",
            "end_date": "2025-04-28",
            "total_silver": 100.50
        }
        response = client.post("/v1/job", json=new_job)
        data = response.get_json()

        expected_response = {
            "code": 422,
            "errors": {
                "json": {
                    "total_silver": [
                        "Value cannot have decimals."
                    ]
                }
            },
            "status": "Unprocessable Entity"
        }

        assert response.status_code == 422
        assert data == expected_response


    def test_post_job_sqlalchemy_error(self, client, monkeypatch):
        """
        Tests that a 500 response with a message is returned if the POST raises a SQLAlchemyError.
        """
        # Monkeypatch db.session.commit to raise SQLAlchemyError
        def bad_commit():
            raise SQLAlchemyError("DB error")

        monkeypatch.setattr(db.session, "commit", bad_commit)

        new_job = {
            "job_name": "job Name",
            "start_date": "2025-01-01",
        }
        response = client.post("/v1/job", json=new_job)

        assert response.status_code == 500
        data = response.get_json()
        assert "An error occurred when inserting to db" in data["message"]


    def test_post_job_generic_error(self, client, sample_ranks, monkeypatch):
        """
        Tests that a 500 response with a message is returned if the POST raises any other error.
        """
        def bad_commit():
            raise RuntimeError("Something went wrong!")

        monkeypatch.setattr(db.session, "commit", bad_commit)

        new_job = {
            "job_name": "job Name",
            "start_date": "2025-01-01",
        }
        response = client.post("/v1/job", json=new_job)
        assert response.status_code == 500
        data = response.get_json()
        assert "Something went wrong!" in data["message"] 


class TestGetJobsErrors:
    def test_get_jobs_by_invalid_date(self, client):
            """
            Tests that it errors if an invalid start_date arg is passed.
            """
            response = client.get("/v1/jobs?start_date=2025")

            expected_response = {
                "code": 422,
                "errors": {
                    "query": {
                        "start_date": [
                            "Not a valid date."
                        ]
                    }
                },
                "status": "Unprocessable Entity"
            }

            assert response.status_code == 422
            assert response.get_json() == expected_response

    def test_get_job_with_invalid_id(self, client):
        """
        Tests that a 422 response is returned if the GET has an invalid job id.
        """
        response = client.get("/v1/job/abc")

        assert response.status_code == 400
        assert response.get_json() ==  {
            "code": 400,
            "message": "Invalid job id",
            "status": "Bad Request"
        }

    def test_get_job_when_id_doesnt_exist(self, client):
        """
        Tests that a 404 response is returned if the GET has a job id that doesn't exist.
        """
        response = client.get(f"/v1/job/{uuid4()}")
        assert response.status_code == 404
        assert response.get_json() ==  {
            "code": 404,
            "status": "Not Found"
        }


@pytest.mark.usefixtures("sample_jobs")
class TestDeleteJobErrors:
    """
        Tests that a user cannot delete a job if they provide invalid details.
    """
    def test_delete_job_that_doesnt_exist(self, client):
        response = client.delete("/v1/job/99")
        assert response.status_code == 400
        assert response.get_json() ==  {
            "code": 400,
            "message": "Invalid job id",
            "status": "Bad Request"
        }

    def test_delete_job_without_id(self, client):
        response = client.delete("/v1/job")
        assert response.status_code == 405
        assert response.get_json() ==  {
            "code": 405,
            "status": "Method Not Allowed"
        }

    def test_delete_job_sqlalchemy_error(self, client, sample_jobs, monkeypatch):
        # Monkeypatch db.session.commit to raise SQLAlchemyError
        def bad_commit():
            raise SQLAlchemyError("DB error")

        monkeypatch.setattr(db.session, "commit", bad_commit)

        id = sample_jobs[0].id 
        response = client.delete(f"/v1/job/{id}")

        assert response.status_code == 500
        data = response.get_json()
        assert "An error occurred when inserting to db" in data["message"]

    
    def test_delete_job_generic_error(self, client, sample_jobs, monkeypatch):
        def bad_commit():
            raise RuntimeError("Something went wrong!")

        monkeypatch.setattr(db.session, "commit", bad_commit)

        id = sample_jobs[0].id 
        response = client.delete(f"/v1/job/{id}")
        
        assert response.status_code == 500
        data = response.get_json()
        assert "Something went wrong!" in data["message"] 


###################################################################################################
#  End of file.
###################################################################################################
