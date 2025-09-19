"""
This module contains a unit test for the rank & ranks endpoint resource in the `src.api.v1/rank_routes` module.
"""

## TODO: refactor tests to remove hardcoded values where possible
## TODO: refactor tests to use fixtures where possible
## TODO: review if util functions can be used to reduce code duplication

###################################################################################################
#  IMPORTS
###################################################################################################

import pytest

from flask import current_app

from constants import DEFAULT_RANK # type: ignore
from src.api.models import RankModel # type: ignore


###################################################################################################
#  HAPPY PATHS : post, get all, get one, update, delete
###################################################################################################


class TestPostRank:
    def test_post_rank(self, client):
        """
        Tests that a user can post a new rank to the API.
        """
        new_rank = {
            "name": "Test Rank",
            "position": 1,
            "share": 0.1
        }
        response = client.post("/v1/rank", json=new_rank)
        data = response.get_json()

        assert response.status_code == 201
        assert data["id"] == data["id"]  # Check that an id is returned
        assert data["name"] == new_rank["name"]
        assert data["position"] == new_rank["position"]
        assert data["share"] == new_rank["share"]

        # fetch the actual model from the DB
        rank = RankModel.query.get(data["id"])

        expected_repr = f"<RankModel(id={data["id"]}, name='Test Rank', position=1, share=0.1)>"
        assert repr(rank) == expected_repr


@pytest.mark.usefixtures("sample_ranks")
class TestGetRankByName:
    def test_get_rank_by_name(self, client):
        """
        Test that a user can get a rank by name
        """
        response = client.get("/v1/rank?name=Captain")
        print(f"response {response.json}")

        assert response.status_code == 200
        assert len(response.get_json()) == 1
        data = response.get_json()[0] # it should only return one, but it returns it as a dict
        # assert isinstance(data, list)
        assert len(data) == 4 # has 4 elements to it 

        ## TODO: work out a better way for this
        # so I've an assertion to make sure the required keys are there
        required_keys = {"id", "name", "position", "share"}
        assert required_keys.issubset(data.keys())
        # and one to make sure the values are correct because id is a uuid
        assert data["name"] == "Captain"
        assert data["position"] == 1
        assert data["share"] == 1.0


@pytest.mark.usefixtures("sample_ranks")
class TestGetRankByPosition:
    def test_get_rank_by_position(self, client):
        """
        Test that a user can get a rank by name
        """
        response = client.get("/v1/rank?position=2")
        print(f"response {response.json}")

        assert response.status_code == 200
        assert len(response.get_json()) == 1
        data = response.get_json()[0] # it should only return one, but it returns it as a dict
        # assert isinstance(data, list)
        assert len(data) == 4 # has 4 elements to it 

         ## TODO: work out a better way for this
        # so I've an assertion to make sure the required keys are there
        required_keys = {"id", "name", "position", "share"}
        assert required_keys.issubset(data.keys())
        # and one to make sure the values are correct because id is a uuid
        assert data["name"] == "Lieutenant"
        assert data["position"] == 2
        assert data["share"] == 1.0


@pytest.mark.usefixtures("sample_ranks")
class TestGetRankById:
    def test_get_rank_by_id(self, client, sample_ranks):
        """
        Test that a user can get a rank by id
        """
        id = sample_ranks[0].id # Get the id of the first sample rank (Captain)
        response = client.get(f"/v1/rank/{id}")

        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 4 # has 4 elements to it 

         ## TODO: work out a better way for this
        # so I've an assertion to make sure the required keys are there
        required_keys = {"id", "name", "position", "share"}
        assert required_keys.issubset(data.keys())
        # and one to make sure the values are correct because id is a uuid
        assert data["name"] == "Captain"
        assert data["position"] == 1
        assert data["share"] == 1.0


## TODO: refactor and paramaterise this so that common code is not duplicated, we can pass in what is to be PATCHed
@pytest.mark.usefixtures("sample_ranks")
class TestUpdateRank:
    def test_update_rank(self, client, sample_ranks):
        """
        Tests that a user can update a rank in the API.
        """
        id = sample_ranks[0].id # Get the id of the first sample rank (Captain)

        # verify details of the rank before updates
        ## TODO: consider using get by id endpoint
        original_response = client.get("/v1/rank?name=Captain")
        original_data = original_response.get_json()[0] # it should only return one, but it returns it as a dict
        original_expected_response = {
            "id": original_data["id"],
            "name": "Captain",
            "position": 1,
            "share": 1.0
        }
        assert original_data == original_expected_response

        # update the rank
        updated_rank = {
            "name": "Updated Rank",
            "position": len(sample_ranks) + 1,
            "share": 0.5
        }
        update_response = client.patch(f"/v1/rank/{id}", json=updated_rank)
        updated_expected_response = {
            "id": original_data["id"], # id should remain the same
            "name": "Updated Rank",
            "position": len(sample_ranks) + 1,
            "share": 0.5
        }
        assert update_response.status_code == 200
        assert update_response.get_json() == updated_expected_response

        # verify Captain is no longer there, but Updated Rank is
        new_get_response = client.get("/v1/ranks")
        new_data = new_get_response.get_json()

        assert original_data not in new_data
        assert updated_expected_response in new_data

    def test_update_rank_name_only(self, client, sample_ranks):
        """
        Tests that a user can update a rank in the API.
        """
        id = sample_ranks[0].id # Get the id of the first sample rank (Captain)

        # verify details of the rank before updates
        ## TODO: consider using get by id endpoint
        original_response = client.get("/v1/rank?name=Captain")
        original_data = original_response.get_json()[0] # it should only return one, but it returns it as a dict
        original_expected_response = {
            "id": original_data["id"],
            "name": "Captain",
            "position": 1,
            "share": 1.0
        }
        assert original_data == original_expected_response

        # update the rank
        updated_rank = {
            "name": "Updated Rank"
        }
        update_response = client.patch(f"/v1/rank/{id}", json=updated_rank)
        updated_expected_response = {
            "id": original_data["id"], # id should remain the same
            "name": "Updated Rank",
            "position": original_data["position"], # position should remain the same
            "share": original_data["share"] # share should remain the same
        }
        assert update_response.status_code == 200
        assert update_response.get_json() == updated_expected_response

        # verify Captain is no longer there, but Updated Rank is
        new_get_response = client.get("/v1/ranks")
        new_data = new_get_response.get_json()

        assert original_data not in new_data
        assert updated_expected_response in new_data

    def test_update_rank_position_only(self, client, sample_ranks):
        """
        Tests that a user can update a rank in the API.
        """
        id = sample_ranks[0].id # Get the id of the first sample rank (Captain)

        # verify details of the rank before updates
        ## TODO: consider using get by id endpoint
        original_response = client.get("/v1/rank?name=Captain")
        original_data = original_response.get_json()[0] # it should only return one, but it returns it as a dict
        original_expected_response = {
            "id": original_data["id"],
            "name": "Captain",
            "position": 1,
            "share": 1.0
        }
        assert original_data == original_expected_response

        # update the rank
        updated_rank = {
            "position": 5
        }
        update_response = client.patch(f"/v1/rank/{id}", json=updated_rank)
        updated_expected_response = {
            "id": original_data["id"], # id should remain the same
            "name": original_data["name"], # name should remain the same
            "position": 5, # position should remain the same
            "share": original_data["share"] # share should remain the same
        }
        assert update_response.status_code == 200
        assert update_response.get_json() == updated_expected_response

        # verify Captain is no longer there, but Updated Rank is
        new_get_response = client.get("/v1/ranks")
        new_data = new_get_response.get_json()

        assert original_data not in new_data
        assert updated_expected_response in new_data

    def test_update_rank_share_only(self, client, sample_ranks):
        """
        Tests that a user can update a rank in the API.
        """
        id = sample_ranks[0].id # Get the id of the first sample rank (Captain)

        # verify details of the rank before updates
        ## TODO: consider using get by id endpoint
        original_response = client.get("/v1/rank?name=Captain")
        original_data = original_response.get_json()[0] # it should only return one, but it returns it as a dict
        original_expected_response = {
            "id": original_data["id"],
            "name": "Captain",
            "position": 1,
            "share": 1.0
        }
        assert original_data == original_expected_response

        # update the rank
        updated_rank = {
            "share": 1.5
        }
        update_response = client.patch(f"/v1/rank/{id}", json=updated_rank)
        updated_expected_response = {
            "id": original_data["id"], # id should remain the same
            "name": original_data["name"], # name should remain the same
            "position": original_data["position"], # position should remain the same
            "share": 1.5 # share should remain the same
        }
        assert update_response.status_code == 200
        assert update_response.get_json() == updated_expected_response

        # verify Captain is no longer there, but Updated Rank is
        new_get_response = client.get("/v1/ranks")
        new_data = new_get_response.get_json()

        assert original_data not in new_data
        assert updated_expected_response in new_data

    def test_update_rank_position_and_share_only(self, client, sample_ranks):
        """
        Tests that a user can update a rank in the API.
        """
        id = sample_ranks[0].id # Get the id of the first sample rank (Captain)

        # verify details of the rank before updates
        ## TODO: consider using get by id endpoint
        original_response = client.get("/v1/rank?name=Captain")
        original_data = original_response.get_json()[0] # it should only return one, but it returns it as a dict
        original_expected_response = {
            "id": original_data["id"],
            "name": "Captain",
            "position": 1,
            "share": 1.0
        }
        assert original_data == original_expected_response

        # update the rank
        updated_rank = {
            "position": 7,
            "share": 1.5
        }
        update_response = client.patch(f"/v1/rank/{id}", json=updated_rank)
        updated_expected_response = {
            "id": original_data["id"], # id should remain the same
            "name": original_data["name"], # name should remain the same
            "position": 7, # position should remain the same
            "share": 1.5 # share should remain the same
        }
        assert update_response.status_code == 200
        assert update_response.get_json() == updated_expected_response

        # verify Captain is no longer there, but Updated Rank is
        new_get_response = client.get("/v1/ranks")
        new_data = new_get_response.get_json()

        assert original_data not in new_data
        assert updated_expected_response in new_data

    ## TODO: add combo of name/position, name/share once paramaterised


@pytest.mark.usefixtures("sample_ranks")
class TestDeleteRank:
    def test_delete_rank(self, client, sample_ranks):
        """
        Tests that a user can delete a rank in the API.
        """
        id = sample_ranks[0].id # Get the id of the first sample rank (Captain)

        # verify details of the rank before updates
        ## TODO: consider using get by id endpoint
        original_response = client.get("/v1/rank?name=Captain")
        original_data = original_response.get_json()[0] # it should only return one, but it returns it as a dict
        original_expected_response = {
            "id": original_data["id"],
            "name": "Captain",
            "position": 1,
            "share": 1.0
        }
        assert original_data == original_expected_response

        # delete the rank
        delete_response = client.delete(f"/v1/rank/{id}")
        assert delete_response.status_code == 200
        assert delete_response.get_json() == {"message": f"Rank id {id} deleted" }

        # verify Captain is no longer there
        new_get_response = client.get("/v1/ranks")
        new_data = new_get_response.get_json()
        assert original_data not in new_data


## These tests need ranks to exist, so we reseed the db before each with sample_ranks
@pytest.mark.usefixtures("sample_ranks")
class TestGetAllRanks:
    def test_get_all_ranks(self, client, sample_ranks):
        """
        Tests that a user can get all ranks.
        These should be returned in position order.
        """
        response = client.get("/v1/ranks")

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)

        expected_response = [
            {
                "id": data[0]["id"], # id is a uuid so we can't hardcode it, but we can check it exists
                "name": sample_ranks[0].name,
                "position": sample_ranks[0].position,
                "share": sample_ranks[0].share 
            },
            {
                "id": data[1]["id"],
                "name": sample_ranks[1].name,
                "position": sample_ranks[1].position,
                "share": sample_ranks[1].share 
            },
            {
                "id": data[2]["id"],
                "name": sample_ranks[2].name,
                "position": sample_ranks[2].position,
                "share": sample_ranks[2].share 
            },
            {
                "id": data[3]["id"],
                "name": sample_ranks[3].name,
                "position": sample_ranks[3].position,
                "share": sample_ranks[3].share 
            },
            { # default rank should always return as the last rank here
                "id": str(DEFAULT_RANK["id"]),
                "name": 'default',
                "position": 99,
                "share": 0 
            }
        ]
        assert data == expected_response


class TestGetAllRanksWhenNoneExist:
    def test_get_all_ranks_when_none_exist(self, client):
        """
        Tests that getting all ranks when none exist returns an empty list.
        """
        result = client.get("/v1/ranks")

        assert result.status_code == 200
        # the database is seeded with the default rank so it ALWAYS exists
        assert result.json == [
            {
                "id": str(DEFAULT_RANK["id"]),
                "name": DEFAULT_RANK["name"],
                "position": DEFAULT_RANK["position"],
                "share": DEFAULT_RANK["share"]
            }
        ]
        

###################################################################################################
#  End of file.
###################################################################################################
