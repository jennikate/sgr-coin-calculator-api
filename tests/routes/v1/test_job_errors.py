"""
This module contains a unit test for the job & job endpoint resource in the `src.api.v1/job_routes` module.
"""

## TODO: refactor tests to remove hardcoded values where possible
## TODO: refactor tests to use fixtures where possible
## TODO: review if util functions can be used to reduce code duplication

###################################################################################################
#  IMPORTS
###################################################################################################

import pytest

from flask import current_app

from src.api.models import JobModel # type: ignore


###################################################################################################
#  ERRORS
###################################################################################################


class TestPostJob:
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
                        "Not a valid number."
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
                        "total_silver cannot have decimals."
                    ]
                }
            },
            "status": "Unprocessable Entity"
        }

        assert response.status_code == 422
        assert data == expected_response


###################################################################################################
#  End of file.
###################################################################################################
