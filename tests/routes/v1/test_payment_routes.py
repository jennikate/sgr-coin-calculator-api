"""
This module contains test for /payments endpoint from the `src.api.v1/job_routes` module.
"""

###################################################################################################
#  IMPORTS
###################################################################################################

import pytest

from constants import COMPANY_CUT # type: ignore


###################################################################################################
#  HAPPY PATHS : note staticmethod is also tested as a pure function in test_payment_methods
###################################################################################################

@pytest.mark.usefixtures("job_with_members")
class TestGetPayments:
    def test_get_job_response_and_pay(self, client, job_with_members):
        """
        Full integration test:
        - Hit GET /v1/job/<job_id>/payments
        - Validate the response structure matches JobResponseSchema
        - Validate member_pay and other calculated fields
        """

        job = job_with_members["job"]
        job_id = job_with_members["job_id"]
        members = job_with_members["members"]

        response = client.get(f"/v1/job/{job_id}/payments")
        assert response.status_code == 200

        data = response.get_json()

        # Validate calculated values
        # Company cut
        expected_company_cut = job.total_silver * COMPANY_CUT
        assert data["company_cut_amt"] == expected_company_cut

        # Value per share
        total_shares = sum(m.rank.share for m in members if m.rank)
        value_per_share = (job.total_silver - expected_company_cut) / total_shares

        # Member pay
        for idx, jm in enumerate(data["members_on_job"]):
            expected_pay = int(members[idx].rank.share * value_per_share)
            assert jm["member_pay"] == expected_pay

        # Remainder after payouts
        total_paid = sum(int(m.rank.share * value_per_share) for m in members)
        expected_remainder = job.total_silver - expected_company_cut - total_paid
        assert data["remainder_after_payouts"] == expected_remainder

        # Validate expected response
        expected_members = [
            {
                "member_id": str(m.id),
                "member_name": m.name,
                "member_pay": int(m.rank.share * value_per_share),
                "member_rank": m.rank.name,
                "member_rank_position": m.rank.position
            }
            for m in [members[0], members[1], members[2]]
        ]

        expected_response = {
            "company_cut_amt": int(expected_company_cut), # is returned as an INT
            "id": str(job_id),
            "job_name": job_with_members["job"].job_name,
            "job_description": job_with_members["job"].job_description,
            "members_on_job": expected_members,
            "remainder_after_payouts": int(expected_remainder),
            "start_date": str(job_with_members["job"].start_date),
            "end_date": str(job_with_members["job"].end_date),
            "total_silver": job_with_members["job"].total_silver
        }

        assert response.status_code == 200
        assert response.get_json() == expected_response

###################################################################################################
#  End of file.
###################################################################################################
