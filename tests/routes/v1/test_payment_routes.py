"""
This module contains test for /payments endpoint from the `src.api.v1/job_routes` module.
"""

## TODO: this test currently tests end point and calculations in one
# refactor this to test the staticmethod alone
# or potentially move static methods to their own file/functions and test as pure function

###################################################################################################
#  IMPORTS
###################################################################################################

import pytest

from constants import COMPANY_CUT # type: ignore
from src.api.models import JobModel # type: ignore


###################################################################################################
#  HAPPY PATHS : post, get all, get one, delete : note updates in their own file
###################################################################################################


# @pytest.mark.usefixtures("sample_jobs")
# class TestGetPayments:
#     def test_get_payment(self, client, job_with_members):
#         """
#         Tests that a user can get a payment for an existing job.
#         """
#         job_id = job_with_members["job_id"]
#         members = job_with_members["members"]

#         response = client.get(f"/v1/job/{job_id}/payments")

#         # calculate the calculated values
#         company_cut_amt = job_with_members["job"].total_silver - (job_with_members["job"].total_silver * COMPANY_CUT)

#         # formt the expected members
#         expected_members = [
#             {
#                 "member_id": str(m.id),
#                 "member_name": m.name,
#                 "member_pay": None,
#                 "member_rank": m.rank.name
#             }
#             for m in [members[0], members[1], members[2]]
#         ]

#         expected_response = {
#             "company_cut_amt": company_cut_amt,
#             "id": str(job_id),
#             "job_name": job_with_members["job"].job_name,
#             "job_description": job_with_members["job"].job_description,
#             "members_on_job": expected_members,
#             "remainder_after_payouts": None,
#             "start_date": str(job_with_members["job"].start_date),
#             "end_date": str(job_with_members["job"].end_date),
#             "total_silver": job_with_members["job"].total_silver
#         }

#         # expected_response =  {
#         #     "company_cut_amt": 10,
#         #     "end_date": "2025-04-28",
#         #     "id": str(job_id),
#         #     "job_description": "For Stromgarde, collecting horns for bounty",
#         #     "job_name": "Ogres in Hinterlands",
#         #     "members_on_job": [
#         #         {
#         #             "member_id": "a23a6f41-23ca-44f3-a0ce-225718b03fd3",
#         #             "member_name": "Bob",
#         #             "member_pay": 32,
#         #             "member_rank": "Captain",
#         #         },
#         #         {
#         #             "member_id": "a045d619-8662-40b1-9086-043860cddcc4",
#         #             "member_name": "Charlie",
#         #             "member_pay": 32,
#         #             "member_rank": "Lieutenant",
#         #         },
#         #         {
#         #             "member_id": "4218e545-fa29-46e6-a5c9-ca163cbbb639",
#         #             "member_name": "Sue",
#         #             "member_pay": 24,
#         #             "member_rank": "Blagguard",
#         #         },
#         #     ],
#         #     "remainder_after_payouts": 2,
#         #     "start_date": "2025-04-23",
#         #     "total_silver": 100,
#         # }

#         assert response.status_code == 200
#         assert response.get_json() == expected_response


###################################################################################################
#  End of file.
###################################################################################################
