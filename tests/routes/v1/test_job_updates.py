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

    def test_update_some_job_fields_and_add_members(self, client, sample_members, sample_jobs):
        """
        Tests that a user can update a job in the API.
        """
        # Get an id to update
        id = sample_jobs[0].id 
        # Get ids of some members to add
        member_id_1 = str(sample_members[0].id)
        member_id_2 = str(sample_members[1].id)
        # Create the update details
        updated_job = {
            "total_silver": 83,
            "add_members": [member_id_1, member_id_2]
        }

        # verify details of the original job are different to the update job
        original_response = client.get(f"/v1/job/{id}")
        assert original_response != updated_job

        # update the job
        update_response = client.patch(f"/v1/job/{id}", json=updated_job)
        updated_expected_response = {
            "company_cut_amt": None, # not updatable as is calculated on GET /payments
            "id": str(sample_jobs[0].id), # id should remain the same
            "job_name": sample_jobs[0].job_name,
            "job_description": sample_jobs[0].job_description,
            "members_on_job": [
                {
                    "member_id": str(sample_members[0].id),
                    "member_name": sample_members[0].name,
                    "member_pay": None, # this is none until we GET /payments
                    "member_rank": sample_members[0].rank.name
                },
                {
                    "member_id": str(sample_members[1].id),
                    "member_name": sample_members[1].name,
                    "member_pay": None, # this is none until we GET /payments
                    "member_rank": sample_members[1].rank.name
                }
            ],
            "remainder_after_payouts": None, # not updatable as is calculated on GET /payments
            "start_date": str(sample_jobs[0].start_date),
            "end_date": str(sample_jobs[0].end_date),
            "total_silver": updated_job["total_silver"]
        }
        assert update_response.status_code == 200
        assert update_response.get_json() == updated_expected_response

###################################################################################################
#  End of file.
###################################################################################################
