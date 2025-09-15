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
#  HAPPY PATHS : updating with members
###################################################################################################

# TODO: extend this to various combinations of things being updated
# including from and to None values
@pytest.mark.usefixtures("sample_jobs")
class TestUpdateJob:
    def test_update_all_updatable_job_fields(self, client, sample_jobs):
        """
        Tests that a user can update a job in the API.
        """
        # Get an id to update
        id = sample_jobs[0].id 
        # Create the update details
        updated_job = {
            "job_name": "New job name",
            "job_description": "New jobs description",
            "start_date": "2026-04-23",
            "end_date": "20260428",
            "total_silver": 7
        }

        # verify details of the original job are different to the update job
        original_response = client.get(f"/v1/job/{id}")
        assert original_response != updated_job

        # update the job
        update_response = client.patch(f"/v1/job/{id}", json=updated_job)
        updated_expected_response = {
            "company_cut_amt": None, # not updatable as is calculated on GET /payments
            "id": original_response.get_json()["id"], # id should remain the same
            "job_name": "New job name",
            "job_description": "New jobs description",
            "members_on_job": [], # updated separately see other tests
            "remainder_after_payouts": None, # not updatable as is calculated on GET /payments
            "start_date": "2026-04-23",
            "end_date": "2026-04-28",
            "total_silver": 7
        }
        assert update_response.status_code == 200
        assert update_response.get_json() == updated_expected_response


###################################################################################################
#  End of file.
###################################################################################################
