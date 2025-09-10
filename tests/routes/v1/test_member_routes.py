"""
Tests for the member & members endpoint resource, located in the `src.api.v1/member_routes` module.
"""

###################################################################################################
#  IMPORTS
###################################################################################################

import pytest

from flask import current_app

from src.api.models import MemberModel, RankModel # type: ignore


###################################################################################################
#  HAPPY PATHS : post, get all, get one, update, delete
###################################################################################################

# This needs a rank to exist for the member to be posted against
@pytest.mark.usefixtures("sample_ranks")
class TestPostMember:
    def test_post_member(self, client, sample_ranks):
        """
        Tests that a user can post a new member to the API.
        """
        rank_id = str(sample_ranks[0].id) # Get the id of the first sample rank & make it a string so we can pass it to the POST
        new_member = {
            "name": "Member Name",
            "rank_id": rank_id,
        }
        
        response = client.post("/v1/member", json=new_member)
        data = response.get_json()

        expected_response = {
            "id": data["id"], # we can't predict the id, so just check it's there
            "name": "Member Name",
            "rank": {
                "id": rank_id,
                "name": "Captain",
                "position": 1,
                "share": 1.0
            },
            "status": True
        }

        assert response.status_code == 201
        assert response.get_json() == expected_response

        # fetch the actual model from the DB
        rank = MemberModel.query.get(data["id"])

        expected_repr = f"<MemberModel(id={data["id"]}, name='Member Name', rank=<RankModel(id={rank_id}, name='Captain', position=1, share=1.0)>)>"
        assert repr(rank) == expected_repr

@pytest.mark.usefixtures("sample_members")
class TestGetMembers:
    def test_get_all_members(self, client, sample_members, sample_ranks):
        """
        Tests that a user can get all members.
        """
        response = client.get("/v1/members")
        data = response.get_json()

        # test the response matches the sample fixtures
        # TODO: can probably loop over this instead of writing it all out
        expected_response = [
            {
                "id": str(sample_members[0].id),
                "name": str(sample_members[0].name),
                "rank": {
                    "id": str(sample_ranks[0].id),
                    "name": str(sample_ranks[0].name),
                    "position": int(sample_ranks[0].position),
                    "share": float(sample_ranks[0].share)
                },
                "status": bool(sample_members[0].status)
            },
            {
                "id": str(sample_members[1].id),
                "name": str(sample_members[1].name),
                "rank": {
                    "id": str(sample_ranks[1].id),
                    "name": str(sample_ranks[1].name),
                    "position": int(sample_ranks[1].position),
                    "share": float(sample_ranks[1].share)
                },
                "status": bool(sample_members[1].status)
            },
            {
                "id": str(sample_members[2].id),
                "name": str(sample_members[2].name),
                "rank": {
                    "id": str(sample_ranks[1].id),
                    "name": str(sample_ranks[1].name),
                    "position": int(sample_ranks[1].position),
                    "share": float(sample_ranks[1].share)
                },
                "status": bool(sample_members[2].status)
            },
        ]

        assert response.status_code == 200
        assert response.get_json() == expected_response

    # def test_get_member_by_id(self, client, sample_members, sample_ranks):
    #     """
    #     Tests that a user can get a member by id.
    #     """
    #     member_id = str(sample_members[0].id)
    #     response = client.get(f"/v1/member/{member_id}")
    #     data = response.get_json()  

    #     expected_response = {
    #         "id": member_id,
    #         "name": str(sample_members[0].name),
    #         "rank": {
    #             "id": str(sample_ranks[0].id),
    #             "name": str(sample_ranks[0].name),
    #             "position": int(sample_ranks[0].position),
    #             "share": float(sample_ranks[0].share)
    #         },
    #         "status": bool(sample_members[0].status)
    #     }
    #     assert response.status_code == 200
    #     assert response.get_json() == expected_response

