"""
Tests for error scenarios for the member & members endpoint resource, located in the `src.api.v1/member_routes` module.
"""

###################################################################################################
#  IMPORTS
###################################################################################################

import pytest

from sqlalchemy.exc import SQLAlchemyError
from uuid import uuid4

from src.extensions import db


###################################################################################################
#  ERROR CASES
###################################################################################################

# This needs a rank to exist for the member to be posted against
@pytest.mark.usefixtures("sample_ranks")
class TestPostMember:
    def test_post_member_no_payload(self, client, sample_ranks):
        """
        Tests that a 422 response is returned if the POST has no payload.
        """
        rank_id = str(sample_ranks[0].id) # Get the id of the first sample rank & make it a string so we can pass it to the POST
        new_member = {}
        
        response = client.post("/v1/member", json=new_member)

        assert response.status_code == 422
        assert response.get_json() ==  {
            "code": 422,
            "errors": {
                "json": {
                    "name": [
                        "Missing data for required field."
                    ],
                    "rank_id": [
                        "Missing data for required field."
                    ]
                }
            },
            "status": "Unprocessable Entity",
        }

    def test_post_member_invalid_fields(self, client, sample_ranks):
        """
        Tests that a 422 response is returned if the POST has invalid fields.
        """
        rank_id = str(sample_ranks[0].id) # Get the id of the first sample rank & make it a string so we can pass it to the POST
        new_member = {
            "name": 7,
            "rank_id": "abc",
        }
        
        response = client.post("/v1/member", json=new_member)
        assert response.status_code == 422
        assert response.get_json() ==  {
            "code": 422,
            "errors": {
                "json": {
                    "name": [
                        "Not a valid string."
                    ],
                    "rank_id": [
                        "Not a valid UUID."
                    ]
                }
            },
            "status": "Unprocessable Entity",
        }

    def test_post_member_name_too_long(self, client, sample_ranks):
        """
        Tests that a 422 response is returned if the POST has a member name that is too long.
        """
        rank_id = str(sample_ranks[0].id) # Get the id of the first sample rank & make it a string so we can pass it to the POST
        new_member = {
            "name": "Member Name is longer than allowed because it is more than 260 charactersMember Name is longer than allowed because it is more than 260 charactersMember Name is longer than allowed because it is more than 260 charactersMember Name is longer than allowed because it is more than 260 charactersMember Name is longer than allowed because it is more than 260 charactersMember Name is longer than allowed because it is more than 260 characters",
            "rank_id": rank_id,
        }
        
        response = client.post("/v1/member", json=new_member)
        assert response.status_code == 422
        assert response.get_json() ==  {
            "code": 422,
            "errors": {
                "json": {
                    "name": [
                        "Name must not exceed 256 characters."
                    ]
                }
            },
            "status": "Unprocessable Entity",
        }

    def test_post_member_name_empty(self, client, sample_ranks):
        """
        Tests that a 422 response is returned if the POST has an empty member name.
        """
        rank_id = str(sample_ranks[0].id) # Get the id of the first sample rank & make it a string so we can pass it to the POST
        new_member = {
            "name": "",
            "rank_id": rank_id,
        }
        
        response = client.post("/v1/member", json=new_member)
        assert response.status_code == 422
        assert response.get_json() ==  {
            "code": 422,
            "errors": {
                "json": {
                    "name": [
                        "Name must not be empty."
                    ]
                }
            },
            "status": "Unprocessable Entity",
        }

    def test_post_member_rank_doesnt_exist(self, client, sample_ranks):
        """
        Tests that a 422 response is returned if the POST has a rank that doesn't exist.
        """
        new_member = {
            "name": "Sample Name",
            "rank_id": uuid4(), # Generate a random UUID that won't exist in the ranks table
        }
        
        response = client.post("/v1/member", json=new_member)
        assert response.status_code == 422
        assert response.get_json() ==  {
            "code": 422,
            "errors": {
                "json": {
                    "rank_id": [
                       f"Rank {new_member["rank_id"]} does not exist"
                    ]
                }
            },
            "status": "Unprocessable Entity",
        }

    def test_post_member_name_exists(self, client, sample_ranks, sample_members):
        """
        Tests that a 422 response is returned if the POST has a member name that already exists.
        """
        # create a new member with the same name as an existing member
        new_member = {
            "name": str(sample_members[1].name), # Get a member name that exists, that isn't the first (so we can apply a different rank)
            "rank_id": str(sample_ranks[0].id) # Get an existing rank that should be different from the existing member's rank
        }
        
        response = client.post("/v1/member", json=new_member)
        data = response.get_json()
        assert response.status_code == 422
        assert response.get_json() ==  {
            "code": 422,
            "errors": {
                "json": {
                    "name": [
                        f"There is already a member with name {new_member["name"]}."
                    ]
                }
            },
            "status": "Unprocessable Entity",
        }

    def test_post_member_sqlalchemy_error(self, client, sample_ranks, monkeypatch):
        """
        Tests that a 500 response with a message is returned if the POST raises a SQLAlchemyError.
        """
        # Monkeypatch db.session.commit to raise SQLAlchemyError
        def bad_commit():
            raise SQLAlchemyError("DB error")

        monkeypatch.setattr(db.session, "commit", bad_commit)

        rank_id = str(sample_ranks[0].id) # Get the id of the first sample rank & make it a string so we can pass it to the POST
        new_member = {
            "name": "Member Name",
            "rank_id": rank_id,
        }
        response = client.post("/v1/member", json=new_member)

        assert response.status_code == 500
        data = response.get_json()
        assert "An error occurred when inserting to db" in data["message"]

    def test_post_member_generic_error(self, client, sample_ranks, monkeypatch):
        """
        Tests that a 500 response with a message is returned if the POST raises any other error.
        """
        def bad_commit():
            raise RuntimeError("Something went wrong!")

        monkeypatch.setattr(db.session, "commit", bad_commit)

        rank_id = str(sample_ranks[0].id) # Get the id of the first sample rank & make it a string so we can pass it to the POST
        new_member = {
            "name": "Member Name",
            "rank_id": rank_id,
        }
        response = client.post("/v1/member", json=new_member)
        assert response.status_code == 500
        data = response.get_json()
        assert "Something went wrong!" in data["message"] 
