"""
This tests that payment data is reset when PATCH updates on the `src.api.v1/job_routes` module.
"""

###################################################################################################
#  IMPORTS
###################################################################################################

import pytest

from constants import COMPANY_CUT, DEFAULT_RANK # type: ignore
from src import db
from tests.test_helpers import assert_job_update


###################################################################################################
#  TESTS
###################################################################################################

@pytest.mark.usefixtures("job_with_members", "sample_members", "sample_jobs") # For every test in this class, automatically run these fixtures before the test starts.
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

    def test_members_added_resets_payment(self, client, job_with_members, sample_members):
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
        
        # Get a member who's not on the job_with_member list
        new_member = next(
        (m for m in sample_members if m.id not in {mj.id for mj in job_with_members["members"]}),
            None
        )
        # Fail the test if all members are present or if only available member has default rank
        assert (new_member is not None and new_member.rank_id is not DEFAULT_RANK["id"]), "Unable to find a sample_member not already on job, without default rank"

        # Create the update details
        updated_job = {
            "add_members": [new_member.id]
        }

        expected_members = [
            {
                "member_id": str(m.id),
                "member_name": m.name,
                "member_pay": None, # this should reset to None for all members
                "member_rank": m.rank.name,
                "member_rank_position": m.rank.position
            }
            for m in members + [new_member] 
            # main test here is the members on the job have None pay value
        ]

        expected_response = {
            "company_cut_amt": None, # should reset to None
            "id": str(job_id), # id should remain the same
            "job_name": data["job_name"], # wasn't updated
            "job_description": data["job_description"], # wasn't updated
            "members_on_job": sorted(expected_members, key=lambda x: (x["member_rank_position"], x["member_name"])),
            "remainder_after_payouts": None, # should reset to None
            "start_date": data["start_date"], # wasn't updated
            "end_date": data["end_date"], # wasn't updated
            "total_silver": data["total_silver"] # wasn't updated
        }
        
        # Call the reusable helper
        assert_job_update(
            client=client,
            job_id=job_id,
            updated_job=updated_job,
            expected_response=expected_response
        )

    def test_members_removed_resets_payment(self, client, job_with_members, sample_members):
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
        
        # Create the update details
        member_to_remove = str(members[1].id)
        updated_job = {"remove_members": [member_to_remove]}

        expected_members = [
            {
                "member_id": str(m.id),
                "member_name": m.name,
                "member_pay": None,
                "member_rank": m.rank.name,
                "member_rank_position": m.rank.position
            }
            for m in [members[0], members[2]]  # only members remaining
        ]

        expected_response = {
            "company_cut_amt": None, # should reset to None
            "id": str(job_id), # id should remain the same
            "job_name": data["job_name"], # wasn't updated
            "job_description": data["job_description"], # wasn't updated
            "members_on_job": sorted(expected_members, key=lambda x: (x["member_rank_position"], x["member_name"])),
            "remainder_after_payouts": None, # should reset to None
            "start_date": data["start_date"], # wasn't updated
            "end_date": data["end_date"], # wasn't updated
            "total_silver": data["total_silver"] # wasn't updated
        }
        
        # Call the reusable helper
        assert_job_update(
            client=client,
            job_id=job_id,
            updated_job=updated_job,
            expected_response=expected_response
        )

    def test_silver_changed_resets_payment(self, client, job_with_members, sample_members):
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
        
        # Create the update details
        new_silver_amt = data["total_silver"] + 100
        updated_job = {"total_silver": new_silver_amt}

        expected_members = [
            {
                "member_id": str(m.id),
                "member_name": m.name,
                "member_pay": None,
                "member_rank": m.rank.name,
                "member_rank_position": m.rank.position
            }
            for m in members
        ]

        expected_response = {
            "company_cut_amt": None, # should reset to None
            "id": str(job_id), # id should remain the same
            "job_name": data["job_name"], # wasn't updated
            "job_description": data["job_description"], # wasn't updated
            "members_on_job": sorted(expected_members, key=lambda x: (x["member_rank_position"], x["member_name"])),
            "remainder_after_payouts": None, # should reset to None
            "start_date": data["start_date"], # wasn't updated
            "end_date": data["end_date"], # wasn't updated
            "total_silver": new_silver_amt
        }
        
        # Call the reusable helper
        assert_job_update(
            client=client,
            job_id=job_id,
            updated_job=updated_job,
            expected_response=expected_response
        )
 
    def test_silver_updated_to_same_value_doesnt_reset_payment(self, client, job_with_members, sample_members):
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
        
        # Create the update details
        updated_job = {"total_silver": data["total_silver"]}

        # Calculate expected member pay 
        # -> this value is only created when we run /payments
        # so has to be manually added to the expected_members
        # otherwise creation of this list will error due to invalid key
        # TODO: Move this calculation to a helper, maybe call it from the code directly 
        # rather than recreating for tests
        # Company cut
        expected_company_cut = data["total_silver"] * COMPANY_CUT
        assert data["company_cut_amt"] == expected_company_cut

        # Value per share
        total_shares = sum(m.rank.share for m in members if m.rank)
        value_per_share = (data["total_silver"] - expected_company_cut) / total_shares

        # Member pay
        for idx, jm in enumerate(data["members_on_job"]):
            expected_pay = int(members[idx].rank.share * value_per_share)
            assert jm["member_pay"] == expected_pay

        expected_members = [
            {
                "member_id": str(m.id),
                "member_name": m.name,
                "member_pay": int(m.rank.share * value_per_share),
                "member_rank": m.rank.name,
                "member_rank_position": m.rank.position
            }
            for m in members
        ]

        expected_response = {
            # everything should remain the same as no actual change was patched
            "company_cut_amt": data["company_cut_amt"],
            "id": str(job_id),
            "job_name": data["job_name"],
            "job_description": data["job_description"],
            "members_on_job": sorted(expected_members, key=lambda x: (x["member_rank_position"], x["member_name"])),
            "remainder_after_payouts": data["remainder_after_payouts"],
            "start_date": data["start_date"],
            "end_date": data["end_date"],
            "total_silver": data["total_silver"]
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
