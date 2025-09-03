"""
This module contains a unit test for the rank & ranks endpoint resource in the `src.api.v1/rank_routes` module.
"""


###################################################################################################
#  Tests
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
        print("Result:", result)

        assert result.status_code == 201
        assert result.json["name"] == "Test Rank"
        assert result.json["position"] == 1
        assert result.json["share"] == 0.1


###################################################################################################
#  End of file.
###################################################################################################
