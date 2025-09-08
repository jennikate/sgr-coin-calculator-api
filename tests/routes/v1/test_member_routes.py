"""
This module contains a unit test for the member & members endpoint resource in the `src.api.v1/member_routes` module.
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

