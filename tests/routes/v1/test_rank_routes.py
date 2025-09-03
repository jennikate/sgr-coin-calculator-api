"""
This module contains a unit test for the rank & ranks endpoint resource in the `src.api.v1/rank_routes` module.
"""

###################################################################################################
#  INITIAL ERRORS : getting all ranks when none exist
###################################################################################################

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


## These tests need ranks to exist, so we can't tear down the db between tests.
class TestGetAllRanks:
    def test_get_all_ranks(self, client, sample_ranks):
        """
        Tests that a user can get all ranks from the API.
        """
        result = client.get("/v1/ranks")

        assert result.status_code == 200
        assert isinstance(result.json, list)
        assert len(result.json) >= 1  # At least one rank should exist



###################################################################################################
#  End of file.
###################################################################################################
