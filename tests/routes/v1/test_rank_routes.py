"""
This module contains a unit test for the rank & ranks endpoint resource in the `src.api.v1/rank_routes` module.
"""

###################################################################################################
#  INITIAL ERRORS : getting all ranks when none exist
###################################################################################################

from tests.utils import assert_response_matches_models


class TestGetAllRanksWhenNoneExist:
    def test_get_all_ranks_when_none_exist(self, client):
        """
        Tests that getting all ranks when none exist returns an empty list.
        """
        result = client.get("/v1/ranks")

        assert result.status_code == 200
        assert result.json == []


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
        result = client.post("/v1/rank", json=new_rank)

        assert result.status_code == 201
        assert result.json["name"] == "Test Rank"
        assert result.json["position"] == 1
        assert result.json["share"] == 0.1


## These tests need ranks to exist, so we reseed the db before each with sample_ranks
class TestGetAllRanks:
    def test_get_all_ranks(self, client, sample_ranks):
        """
        Tests that a user can get all ranks from the API.
        """
        result = client.get("/v1/ranks")

        assert result.status_code == 200
        data = result.get_json()
        assert isinstance(data, list)
        assert len(data) == len(sample_ranks)
        assert_response_matches_models(result, sample_ranks) # this ignores ID's by default so we may want to also assert they're returned

        ## Keeping the longhand here as an example for now
        ## note: id's are returned but we ignore them as they're uuids
        # assert len(data[0]["id"]) >= 1 for when we move to uuid
        assert data[0]["id"] >= 1
        assert data[0]["name"] == "Captain"
        assert data[0]["position"] == 1
        assert data[0]["share"] == 1
        assert data[1]["id"] >= 1
        assert data[1]["name"] == "Lieutenant"
        assert data[1]["position"] == 2
        assert data[1]["share"] == 1
        assert data[2]["id"] >= 1
        assert data[2]["name"] == "Blagguard"
        assert data[2]["position"] == 3
        assert data[2]["share"] == 0.75


class TestGetRankByName:
    def test_get_rank_by_name(self, client, sample_ranks):
        """
        Test that a user can get a rank by name
        """
        result = client.get("/v1/rank?name=Captain")
        print(f"RESULT {result.json}")

        assert result.status_code == 200
        assert len(result.get_json()) == 1
        data = result.get_json()[0] # it should only return one, but it returns it as a dict
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



class TestGetRankByPosition:
    def test_get_rank_by_position(self, client, sample_ranks):
        """
        Test that a user can get a rank by name
        """
        result = client.get("/v1/rank?position=2")
        print(f"RESULT {result.json}")

        assert result.status_code == 200
        assert len(result.get_json()) == 1
        data = result.get_json()[0] # it should only return one, but it returns it as a dict
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

###################################################################################################
#  ERROR PATHS : post, get one, update, delete
###################################################################################################



###################################################################################################
#  End of file.
###################################################################################################
