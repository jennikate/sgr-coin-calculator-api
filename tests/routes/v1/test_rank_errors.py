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

@pytest.mark.usefixtures("sample_ranks")
class TestGetSpecificRankErrors:
    """
        Test that a user cannot get a rank when the query string is invalid
    """
    def test_get_rank_by_name_when_does_not_exist(self, client):
        response = client.get("/v1/rank?name=Sam")
        
        assert response.status_code == 404
        assert response.get_json() ==  {
            "code": 404,
            "message": "No ranks found for name: Sam",
            "status": "Not Found"
        }

    def test_get_rank_by_position_when_does_not_exist(self, client):
        response = client.get("/v1/rank?position=99")
        
        assert response.status_code == 404
        assert response.get_json() ==  {
            "code": 404,
            "message": "No ranks found for position: 99",
            "status": "Not Found"
        }

    def test_get_rank_with_invalid_query_string(self, client):
        response = client.get("/v1/rank?foo=99")
        
        assert response.status_code == 400
        assert response.get_json() ==  {
            "code": 400,
            "message": "At least one query parameter (name or position) must be provided",
            "status": "Bad Request"
        }

    def test_get_rank_with_missing_query_string(self, client):
        response = client.get("/v1/rank")
        
        assert response.status_code == 400
        assert response.get_json() ==  {
            "code": 400,
            "message": "At least one query parameter (name or position) must be provided",
            "status": "Bad Request"
        }
    

    def test_get_rank_with_invalid_position_type(self, client):
        response = client.get("/v1/rank?position=samson")
        
        assert response.status_code == 422
        assert response.get_json() ==  {
            "code": 422,
            "errors": {
                "query": {
                    "position": [
                        "Not a valid integer."
                    ],
                }
            },
            "status": "Unprocessable Entity",
        }
    

    def test_get_rank_with_invalid_name_type(self, client):
        response = client.get("/v1/rank?name=7")
        
        assert response.status_code == 404
        assert response.get_json() ==  {
            "code": 404,
            "message": "No ranks found for name: 7",
            "status": "Not Found"
        }


@pytest.mark.usefixtures("sample_ranks")
class TestUpdateRankErrors:
    """
        Tests that a user cannot update a rank if they provide invalid details.
    """
    def test_update_rank_that_doesnt_exist(self, client):
        updated_rank = {
            "name": "Updated Rank",
            "position": 4,
            "share": 0.5
        }
        response = client.patch(f"/v1/rank/99", json=updated_rank)
        assert response.status_code == 404
        assert response.get_json() ==  {
            "code": 404,
            "status": "Not Found"
        }

    def test_update_rank_with_existing_details(self, client):
        """
            Tests that a user cannot update a rank if they provide an existing name/position.
        """
        # Check rank exists
        response = client.get("/v1/rank?name=Captain")
        assert response.status_code == 200
        data = response.get_json()
        assert any(r["name"] == "Captain" and r["position"] == 1 for r in data)

        # Update with the same details
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


@pytest.mark.usefixtures("sample_ranks")
class TestDeleteRankErrors:
    """
        Tests that a user cannot delete a rank if they provide invalid details.
    """
    def test_delete_rank_that_doesnt_exist(self, client):
        response = client.delete("/v1/rank/99")
        assert response.status_code == 404
        assert response.get_json() ==  {
            "code": 404,
            "status": "Not Found"
        }

    def test_delete_rank_without_id(self, client):
        response = client.delete("/v1/rank")
        assert response.status_code == 405
        assert response.get_json() ==  {
            "code": 405,
            "status": "Method Not Allowed"
        }


###################################################################################################
#  End of file.
###################################################################################################
