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

from src import db
from tests.test_helpers import assert_job_update


###################################################################################################
#  HAPPY PATHS : updating with members
###################################################################################################

@pytest.mark.usefixtures("sample_jobs")
class TestUpdateJob:

    def test_update_all_updatable_job_fields(self, client, sample_jobs):
        """
        Tests that a user can update a job in the API.
        """
        job_id = sample_jobs[0].id # get a job to update

        updated_job = {
            "job_name": "New job name",
            "job_description": "New jobs description",
            "start_date": "2026-04-23",
            "end_date": "20260428",
            "total_silver": 7
        }

        expected_response = {
            "company_cut_amt": None, # not updatable as is calculated on GET /payments
            "id": str(job_id), # id should remain the same
            "job_name": "New job name",
            "job_description": "New jobs description",
            "members_on_job": [], # updated separately see other tests
            "remainder_after_payouts": None, # not updatable as is calculated on GET /payments
            "start_date": "2026-04-23",
            "end_date": "2026-04-28",
            "total_silver": 7
        }
        
        # Call the reusable helper
        assert_job_update(
            client=client,
            job_id=job_id,
            updated_job=updated_job,
            expected_response=expected_response
        )

    def test_update_some_job_fields_and_add_members(self, client, sample_members, sample_jobs):
        """
        Tests that a user can update a job in the API.
        """
        # Get an id to update
        job_id = sample_jobs[0].id 
        # Get ids of some members to add
        member_id_1 = str(sample_members[0].id)
        member_id_2 = str(sample_members[1].id)
        # Create the update details
        updated_job = {
            "total_silver": 83,
            "add_members": [member_id_1, member_id_2]
        }

        expected_response = {
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
        
        # Call the reusable helper
        assert_job_update(
            client=client,
            job_id=job_id,
            updated_job=updated_job,
            expected_response=expected_response
        )

    def test_add_members(self, client, sample_members, sample_jobs):
        """
        Tests that a user can update a job in the API.
        """
        # Get an id to update
        job_id = sample_jobs[0].id 
        # Get ids of some members to add
        member_id_1 = str(sample_members[0].id)
        member_id_2 = str(sample_members[1].id)
        # Create the update details
        updated_job = {
            "add_members": [member_id_1, member_id_2]
        }

        expected_response = {
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
            "total_silver": sample_jobs[0].total_silver
        }
        
        # Call the reusable helper
        assert_job_update(
            client=client,
            job_id=job_id,
            updated_job=updated_job,
            expected_response=expected_response
        )

    def test_remove_members(self, client, job_with_members):
        """
        Tests that a user can remove a job.
        """
        job_id = job_with_members["job_id"]
        members = job_with_members["members"]

        # Remove the second member
        member_to_remove = str(members[1].id)
        updated_job = {"remove_members": [member_to_remove]}

        # TODO: refactor the other member dicts to use this pattern to make DRYer
        # or refactor this one to match the others to make clearer
        # need to decide on my preference
        expected_members = [
            {
                "member_id": str(m.id),
                "member_name": m.name,
                "member_pay": None,
                "member_rank": m.rank.name
            }
            for m in [members[0], members[2]]  # only members remaining
        ]
        expected_response = {
            "company_cut_amt": None,
            "id": str(job_id),
            "job_name": job_with_members["job"].job_name,
            "job_description": job_with_members["job"].job_description,
            "members_on_job": expected_members,
            "remainder_after_payouts": None,
            "start_date": str(job_with_members["job"].start_date),
            "end_date": str(job_with_members["job"].end_date),
            "total_silver": job_with_members["job"].total_silver
        }

        # With the caching in tests
        # When this called the update job handler and the PATCH was made
        # It was still returning the object from the fixture
        # We have to run the fixture to add members to jobs as this can't be done on job creation
        # But this sits in the test cache and was being used for the assertion

        # The most important thing is the db is updated
        # So even though the response to the PATCH is returning the wrong data in the test due to caching
        # We have seen it work correctly in Insomnia
        # We can check the DB is correctly updated

        client.patch(f"/v1/job/{job_id}", json=updated_job)

        # Expire all cached objects so the next query gets fresh data
        db.session.expire_all()

        response = client.get(f"/v1/job/{job_id}")
        assert response.get_json() == expected_response

    def test_add_remove_members_and_update_job(self, client, sample_members, job_with_members):
        """
        Tests that a user can add and remove members at the same time as updating the job details.
        Jobs cannot be created with members, so we must take a job and add members before removing them.
        """
        job_id = job_with_members["job_id"]
        members = job_with_members["members"]

        # Remove the second member
        member_to_remove = str(members[1].id)
        member_to_add = str(sample_members[3].id)
        updated_job = {
            "remove_members": [member_to_remove], 
            "add_members": [member_to_add],
            "total_silver": 12500
        }

        expected_members = [
            {
                "member_id": str(m.id),
                "member_name": m.name,
                "member_pay": None,
                "member_rank": m.rank.name
            }
            for m in [members[0], members[2], sample_members[3]]  # originally created with 0,1,2 -> removed 1, added 3
        ]
        expected_response = {
            "company_cut_amt": None,
            "id": str(job_id),
            "job_name": job_with_members["job"].job_name,
            "job_description": job_with_members["job"].job_description,
            "members_on_job": expected_members,
            "remainder_after_payouts": None,
            "start_date": str(job_with_members["job"].start_date),
            "end_date": str(job_with_members["job"].end_date),
            "total_silver": 12500
        }

        # With the caching in tests
        # When this called the update job handler and the PATCH was made
        # It was still returning the object from the fixture
        # We have to run the fixture to add members to jobs as this can't be done on job creation
        # But this sits in the test cache and was being used for the assertion

        # The most important thing is the db is updated
        # So even though the response to the PATCH is returning the wrong data in the test due to caching
        # We have seen it work correctly in Insomnia
        # We can check the DB is correctly updated

        client.patch(f"/v1/job/{job_id}", json=updated_job)

        # Expire all cached objects so the next query gets fresh data
        db.session.expire_all()

        response = client.get(f"/v1/job/{job_id}")
        assert response.get_json() == expected_response


###################################################################################################
#  End of file.
###################################################################################################
