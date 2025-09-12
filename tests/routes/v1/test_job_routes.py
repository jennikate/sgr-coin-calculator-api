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
#  HAPPY PATHS : post, get all, get one, update, delete
###################################################################################################


class TestPostJob:
    def test_post_job(self, client):
        """
        Tests that a user can post a new job to the API.
        """
        new_job = {
            "job_name": "Ogres in Hinterlands",
            "job_description": "For Stromgarde, collecting horns for bounty",
            "start_date": "2025-04-23",
            "end_date": "2025-04-28",
            "total_silver": 100
        }
        response = client.post("/v1/job", json=new_job)
        data = response.get_json()

        expected_response = {
            "end_date": "2025-04-28",
            "id": data["id"], # UUID is generated
            "job_description": "For Stromgarde, collecting horns for bounty",
            "job_name": "Ogres in Hinterlands",
            "start_date": "2025-04-23",
            "total_silver": 100
        }

        assert response.status_code == 201
        assert data == expected_response

        # fetch the actual model from the DB
        job = JobModel.query.get(data["id"])

        expected_repr = f"""src.api.models.JobModel(company_cut_amt=None, end_date=datetime.date(2025, 4, 28), id=UUID('{data["id"]}'), job_description='For Stromgarde, collecting horns for bounty', job_name='Ogres in Hinterlands', remainder_after_payouts=None, start_date=datetime.date(2025, 4, 23), total_silver=100)"""

        assert repr(job) == expected_repr

    def test_post_job_only_required_fields(self, client):
        """
        Tests that a user can post a new job to the API.
        """
        new_job = {
            "job_name": "Ogres in Hinterlands",
            "start_date": "2025-04-23"
        }
        response = client.post("/v1/job", json=new_job)
        data = response.get_json()

        expected_response = {
            "end_date": None,
            "id": data["id"], # UUID is generated
            "job_description": None,
            "job_name": "Ogres in Hinterlands",
            "start_date": "2025-04-23",
            "total_silver": None
        }

        assert response.status_code == 201
        assert data == expected_response

        # fetch the actual model from the DB
        job = JobModel.query.get(data["id"])

        expected_repr = f"""src.api.models.JobModel(company_cut_amt=None, end_date=None, id=UUID('{data["id"]}'), job_description=None, job_name='Ogres in Hinterlands', remainder_after_payouts=None, start_date=datetime.date(2025, 4, 23), total_silver=None)"""

        assert repr(job) == expected_repr


    def test_post_job_valid_formats(self, client):
        """
        Tests that a user can post a new job to the API using non defined but still valid formats
        """
        new_job = {
            "job_name": "Ogres in Hinterlands",
            "job_description": "For Stromgarde, collecting horns for bounty",
            "start_date": "20250423", # should be converted by smorest/Marshmallow to a date
            "end_date": "2025/04/28", # should be converted by smorest/Marshmallow to a date
            "total_silver": "100" # should be converted by smorest/Marshmallow to an int
        }
        response = client.post("/v1/job", json=new_job)
        data = response.get_json()

        expected_response = {
            "end_date": "2025-04-28",
            "id": data["id"], # UUID is generated
            "job_description": "For Stromgarde, collecting horns for bounty",
            "job_name": "Ogres in Hinterlands",
            "start_date": "2025-04-23",
            "total_silver": 100
        }

        assert response.status_code == 201
        assert data == expected_response

        # fetch the actual model from the DB
        job = JobModel.query.get(data["id"])

        expected_repr = f"""src.api.models.JobModel(company_cut_amt=None, end_date=datetime.date(2025, 4, 28), id=UUID('{data["id"]}'), job_description='For Stromgarde, collecting horns for bounty', job_name='Ogres in Hinterlands', remainder_after_payouts=None, start_date=datetime.date(2025, 4, 23), total_silver=100)"""

        assert repr(job) == expected_repr


###################################################################################################
#  End of file.
###################################################################################################
