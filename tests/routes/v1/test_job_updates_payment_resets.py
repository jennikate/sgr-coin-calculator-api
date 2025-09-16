"""
This tests that payment data is reset when PATCH updates on the `src.api.v1/job_routes` module.
"""

###################################################################################################
#  IMPORTS
###################################################################################################

import pytest

from src import db
from tests.test_helpers import assert_job_update


###################################################################################################
#  TESTS
###################################################################################################

@pytest.mark.usefixtures("sample_jobs")
class TestUpdateJob:

    def test_update_non_payment_impacting_fields(self, client, job_with_members):
        """
        Tests that a user can update a job in the API.
        """
        job_id = job_with_members["job_id"]
        members = job_with_members["members"]

        # First run get payments so we apply payment values
        response = client.get(f"/v1/job/{job_id}/payments")
        assert response.status_code == 200

        # make sure company_cut, remainder_after_payouts, and member_pay amounts exist
        data = response.get_json()
        assert data["company_cut_amt"] is not None
        assert data["remainder_after_payouts"] is not None
        assert all(m['member_pay'] is not None for m in data['members_on_job']), \
        "Some members have member_pay = None"

        print(data["members_on_job"])
        
        # update the job with non impacting fields
        updated_job = {
            "job_name": "New job name",
            "job_description": "New jobs description",
            "start_date": "2026-04-23",
            "end_date": "20260428"
        }

        expected_response = {
            "company_cut_amt": data["company_cut_amt"], # should remain as it was originally
            "id": str(job_id), # id should remain the same
            "job_name": "New job name",
            "job_description": "New jobs description",
            "members_on_job": data["members_on_job"], # should remain as it was originally
            "remainder_after_payouts": data["remainder_after_payouts"], # should remain as it was originally
            "start_date": "2026-04-23",
            "end_date": "2026-04-28",
            "total_silver": data["total_silver"] # was not changed in our update
        }
        
        # Call the reusable helper
        assert_job_update(
            client=client,
            job_id=job_id,
            updated_job=updated_job,
            expected_response=expected_response
        )



###################################################################################################
#  End of file.
###################################################################################################
