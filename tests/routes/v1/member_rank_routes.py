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
        print("------------- Testing POST /v1/member endpoint -------------")
        id = str(sample_ranks[0].id) # Get the id of the first sample rank & make it a string so we can pass it to the POST
        print(f"Using rank id: {id} for the new member")
        new_member = {
            "name": "Member Name",
            "rank_id": id,
        }
        print(f"Using details: {new_member} for the new member")
        response = client.post("/v1/member", json=new_member)
        data = response.get_json()
        print(f"Response data: {data}")

        # assert response.status_code == 201
        # current_app.logger.info(f"Response data: {data}")
        # assert data["id"] == data["id"]  # Check that an id is returned
        # assert data["name"] == "Member Name"
        # assert data["status"] == True
        # assert data["rank"] == id

        # # fetch the actual model from the DB
        # rank = MemberModel.query.get(data["id"])

        # expected_repr = f"<RankModel(id={data["id"]}, name='Test Rank', position=1, share=0.1)>"
        # assert repr(rank) == expected_repr
