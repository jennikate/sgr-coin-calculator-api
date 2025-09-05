"""
This module contains a unit test for the rank & ranks endpoint resource in the `src.api.v1/rank_routes` module.
"""

## TODO: refactor tests to remove hardcoded values where possible
## TODO: refactor tests to use fixtures where possible
## TODO: review if util functions can be used to reduce code duplication

###################################################################################################
#  IMPORTS
###################################################################################################

from flask import current_app
import pytest

from tests.utils import assert_response_matches_models


###################################################################################################
#  ERROR CASES
###################################################################################################

class TestGetAllRanksWhenNoneExist:
    def test_get_all_ranks_when_none_exist(self, client):
        """
        Tests that getting all ranks when none exist returns an empty list.
        """
        result = client.get("/v1/ranks")

        assert result.status_code == 200
        assert result.json == []


class TestPostRankErrors:
    def test_post_rank_no_name(self, client):
        """
        Tests the correct error shows when posting a rank with no name.
        """
        new_rank = {
            "position": 1,
            "share": 0.1
        }
        response = client.post("/v1/rank", json=new_rank)

        assert response.status_code == 422
        assert response.get_json() ==  {
            "code": 422,
            "errors": {
                "json": {
                    "name": [
                        "Missing data for required field."
                    ]
                }
            },
            "status": "Unprocessable Entity",
        }

    def test_post_rank_no_position(self, client):
        """
        Tests the correct error shows when posting a rank with no name.
        """
        new_rank = {
            "name": "Captain",
            "share": 0.1
        }
        response = client.post("/v1/rank", json=new_rank)

        assert response.status_code == 422
        assert response.get_json() ==  {
            "code": 422,
            "errors": {
                "json": {
                    "position": [
                        "Missing data for required field."
                    ]
                }
            },
            "status": "Unprocessable Entity",
        }

    def test_post_rank_no_share(self, client):
        """
        Tests the correct error shows when posting a rank with no name.
        """
        new_rank = {
            "position": 1,
            "name": "Captain"
        }
        response = client.post("/v1/rank", json=new_rank)

        assert response.status_code == 422
        assert response.get_json() ==  {
            "code": 422,
            "errors": {
                "json": {
                    "share": [
                        "Missing data for required field."
                    ]
                }
            },
            "status": "Unprocessable Entity",
        }

    def test_post_rank_no_fields(self, client):
        """
        Tests the correct error shows when posting a rank with no name.
        """
        new_rank = {}
        response = client.post("/v1/rank", json=new_rank)

        assert response.status_code == 422
        assert response.get_json() ==  {
            "code": 422,
            "errors": {
                "json": {
                    "name": [
                        "Missing data for required field."
                    ],
                    "position": [
                        "Missing data for required field."
                    ],
                    "share": [
                        "Missing data for required field."
                    ]
                }
            },
            "status": "Unprocessable Entity",
        }

    def test_post_rank_invalid_types(self, client):
        """
        Tests the correct error shows when posting a rank with no name.
        """
        new_rank = {
            "name": 1,
            "position": "badtype",
            "share": "badtype"
        }
        response = client.post("/v1/rank", json=new_rank)

        assert response.status_code == 422
        assert response.get_json() ==  {
            "code": 422,
            "errors": {
                "json": {
                    "name": [
                        "Not a valid string."
                    ],
                    "position": [
                        "Not a valid integer."
                    ],
                    "share": [
                        "Not a valid number."
                    ]
                }
            },
            "status": "Unprocessable Entity",
        }

@pytest.mark.usefixtures("sample_ranks")
class TestPostRankAlreadyExists:
    def test_post_rank_already_exists(self, client):
        """
        Test that a user cannot post a rank where the name and/or position already exists
        """
        # Check rank exists
        response = client.get("/v1/rank?name=Captain")
        assert response.status_code == 200
        data = response.get_json()
        assert any(r["name"] == "Captain" and r["position"] == 1 for r in data)

        # Post with the same details
        new_rank = {
            "name": "Captain",
            "position": 1,
            "share": 1.5
        }
        response = client.post("/v1/rank", json=new_rank)

        assert response.status_code == 422
        assert response.get_json() ==  {
            "code": 422,
            "errors": {
                "json": {
                    "name": [
                        f"There is already a rank with name {new_rank["name"]}."
                    ],
                    "position": [
                        f"There is already a rank at position {new_rank["position"]}."
                    ]
                }
            },
            "status": "Unprocessable Entity",
        }


###################################################################################################
#  ERROR PATHS : post, get one, update, delete
###################################################################################################



###################################################################################################
#  End of file.
###################################################################################################
