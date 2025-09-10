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
        assert data == expected_response

        # fetch the actual model from the DB
        rank = MemberModel.query.get(data["id"])

        expected_repr = f"<MemberModel(id={data["id"]}, name='Member Name', rank=<RankModel(id={rank_id}, name='Captain', position=1, share=1.0)>)>"
        assert repr(rank) == expected_repr

@pytest.mark.usefixtures("sample_members", "sample_ranks")
class TestGetMembers:
    def test_get_all_members(self, client, sample_members, sample_ranks):
        """
        Tests that a user can get all members, sorted by rank then name.
        """
        response = client.get("/v1/members")

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
                "id": str(sample_members[3].id),
                "name": str(sample_members[3].name),
                "rank": {
                    "id": str(sample_ranks[2].id),
                    "name": str(sample_ranks[2].name),
                    "position": int(sample_ranks[2].position),
                    "share": float(sample_ranks[2].share)
                },
                "status": bool(sample_members[3].status)
            },
            {
                "id": str(sample_members[2].id),
                "name": str(sample_members[2].name),
                "rank": {
                    "id": str(sample_ranks[2].id),
                    "name": str(sample_ranks[2].name),
                    "position": int(sample_ranks[2].position),
                    "share": float(sample_ranks[2].share)
                },
                "status": bool(sample_members[2].status)
            },
        ]

        assert response.status_code == 200
        assert response.get_json() == expected_response

    def test_get_all_members_by_rank(self, client, sample_members, sample_ranks):
        """
        Tests that a user can get all members for a specific rank.
        """
        response = client.get("/v1/members?rank=" + str(sample_ranks[2].id))

        # test the response matches the sample fixtures
        # TODO: can probably loop over this instead of writing it all out
        expected_response = [
            {
                "id": str(sample_members[3].id),
                "name": str(sample_members[3].name),
                "rank": {
                    "id": str(sample_ranks[2].id),
                    "name": str(sample_ranks[2].name),
                    "position": int(sample_ranks[2].position),
                    "share": float(sample_ranks[2].share)
                },
                "status": bool(sample_members[3].status)
            },
            {
                "id": str(sample_members[2].id),
                "name": str(sample_members[2].name),
                "rank": {
                    "id": str(sample_ranks[2].id),
                    "name": str(sample_ranks[2].name),
                    "position": int(sample_ranks[2].position),
                    "share": float(sample_ranks[2].share)
                },
                "status": bool(sample_members[2].status)
            },
        ]

        assert response.status_code == 200
        assert response.get_json() == expected_response


    def test_get_all_members_by_rank_no_members(self, client, sample_members, sample_ranks):
        """
        Tests that a user can get all members for a specific rank.
        """
        response = client.get("/v1/members?rank=" + str(sample_ranks[len(sample_ranks) -1].id))
        expected_response = [] # empty list

        assert response.status_code == 200
        assert response.get_json() == expected_response

    def test_get_all_members_sort_order(self, client, sample_members, sample_ranks):
        """
        Tests that a user can get all members, sorted by rank then name.
        """
        # add another member that would break the original sort order if not sorted correctly
        new_member = {
            "name": "A Member Name",
            "rank_id": str(sample_ranks[1].id) ,
        }
        
        post_response = client.post("/v1/member", json=new_member)

        # Get all members
        response = client.get("/v1/members")
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
                "id": post_response.get_json()["id"],
                "name": "A Member Name",
                "rank": {
                    "id": str(sample_ranks[1].id),
                    "name": str(sample_ranks[1].name),
                    "position": int(sample_ranks[1].position),
                    "share": float(sample_ranks[1].share)
                },
                "status": bool(sample_members[1].status)
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
                "id": str(sample_members[3].id),
                "name": str(sample_members[3].name),
                "rank": {
                    "id": str(sample_ranks[2].id),
                    "name": str(sample_ranks[2].name),
                    "position": int(sample_ranks[2].position),
                    "share": float(sample_ranks[2].share)
                },
                "status": bool(sample_members[3].status)
            },
            {
                "id": str(sample_members[2].id),
                "name": str(sample_members[2].name),
                "rank": {
                    "id": str(sample_ranks[2].id),
                    "name": str(sample_ranks[2].name),
                    "position": int(sample_ranks[2].position),
                    "share": float(sample_ranks[2].share)
                },
                "status": bool(sample_members[2].status)
            },
        ]

        assert response.status_code == 200
        assert response.get_json() == expected_response

    def test_get_member_by_id(self, client, sample_members, sample_ranks):
        """
        Tests that a user can get a member by id.
        """
        member_id = str(sample_members[0].id)
        response = client.get(f"/v1/member/{member_id}")
        data = response.get_json()  

        expected_response = {
            "id": member_id,
            "name": str(sample_members[0].name),
            "rank": {
                "id": str(sample_ranks[0].id),
                "name": str(sample_ranks[0].name),
                "position": int(sample_ranks[0].position),
                "share": float(sample_ranks[0].share)
            },
            "status": bool(sample_members[0].status)
        }
        assert response.status_code == 200
        assert response.get_json() == expected_response


@pytest.mark.usefixtures("sample_members", "sample_ranks")
class TestUpdateMember:
    def test_update_member(self, client, sample_members, sample_ranks):
        """
        Tests that a user can update a member in the API.
        """
        member_id = sample_members[0].id # Get the id of a sample member
        # confirm original is not the one we will update to
        assert sample_members[0].name != "Updated"
        assert sample_members[0].rank_id != sample_ranks[2].id
        assert sample_members[0].status != False

        patch_data = {
            "name": "Updated",
            "rank_id": str(sample_ranks[2].id),
            "status": False
        }

        response = client.patch(f"/v1/member/{member_id}", json=patch_data)
        assert response.status_code == 200
        data = response.get_json()

        expected_result = {
            'id': str(member_id), 
            'name': "Updated", 
            'rank': {
                'id': str(sample_ranks[2].id), 
                'name': str(sample_ranks[2].name), 
                'position': int(sample_ranks[2].position), 
                'share': float(sample_ranks[2].share)
                }, 
            'status': False
        }
        
        assert expected_result == data

    def test_update_member_name_only(self, client, sample_members, sample_ranks):
        """
        Tests that a user can update a member name only in the API.
        """
        member_id = sample_members[0].id
        # confirm original is not the one we will update to
        assert sample_members[0].name != "Updated"
        # get the original member details to assert against
        original_member = client.get(f"/v1/member/{member_id}")

        patch_data = {
            "name": "Updated"
        }

        response = client.patch(f"/v1/member/{member_id}", json=patch_data)
        assert response.status_code == 200
        data = response.get_json()

        expected_result = {
            'id': str(member_id), 
            'name': "Updated", 
            'rank': {
                'id': original_member.get_json()['rank']['id'], 
                'name': original_member.get_json()['rank']['name'], 
                'position': original_member.get_json()['rank']['position'], 
                'share': original_member.get_json()['rank']['share']
                }, 
            'status': original_member.get_json()['status']
        }
        
        assert expected_result == data

    def test_update_member_rank_only(self, client, db, sample_members, sample_ranks):
        """
            Tests that a user can update a member rank only in the API.
        """
        member_id = sample_members[0].id # Get the id of a sample member
        # confirm original is not the one we will update to
        assert sample_members[0].rank_id != sample_ranks[2].id

        patch_data = {
            "rank_id": str(sample_ranks[2].id)
        }

        response = client.patch(f"/v1/member/{member_id}", json=patch_data)
        assert response.status_code == 200
        data = response.get_json()

        expected_result = {
            'id': str(member_id), 
            'name': sample_members[0].name, 
            'rank': {
                'id': str(sample_ranks[2].id), 
                'name': str(sample_ranks[2].name), 
                'position': int(sample_ranks[2].position), 
                'share': float(sample_ranks[2].share)
                }, 
            'status': sample_members[0].status
        }
        
        assert expected_result == data

    
    def test_update_member_status_only(self, client, sample_members, sample_ranks):
        """
            Tests that a user can update a member status only in the API.
        """
        member_id = sample_members[0].id
        # confirm original is not the one we will update to
        assert sample_members[0].name != "Updated"
        # get the original member details to assert against
        original_member = client.get(f"/v1/member/{member_id}")

        patch_data = {
            "status": False
        }

        response = client.patch(f"/v1/member/{member_id}", json=patch_data)
        assert response.status_code == 200
        data = response.get_json()

        expected_result = {
            'id': str(member_id), 
            'name': original_member.get_json()['name'], 
            'rank': {
                'id': original_member.get_json()['rank']['id'], 
                'name': original_member.get_json()['rank']['name'], 
                'position': original_member.get_json()['rank']['position'], 
                'share': original_member.get_json()['rank']['share']
                }, 
            'status': False
        }
        
        assert expected_result == data


@pytest.mark.usefixtures("sample_members", "sample_ranks")
class TestDeleteMember:
    def test_delete_member(self, client, sample_members, sample_ranks):
        """
        Tests that a user can delete a member in the API.
        """
        id = sample_members[1].id # Get the id of a sample member
        # verify details of the member before updates
        original_response = client.get(f"/v1/member/{id}")
        original_expected_response = {
                "id": str(sample_members[1].id),
                "name": str(sample_members[1].name),
                "rank": {
                    "id": str(sample_ranks[1].id),
                    "name": str(sample_ranks[1].name),
                    "position": int(sample_ranks[1].position),
                    "share": float(sample_ranks[1].share)
                },
                "status": bool(sample_members[1].status)
            }
        assert original_response.get_json() == original_expected_response

        # delete the member
        delete_response = client.delete(f"/v1/member/{id}")
        assert delete_response.status_code == 200
        assert delete_response.get_json() == {"message": f"Member id {id} deleted" }

        # verify member is no longer there
        new_get_response = client.get("/v1/members")
        assert original_response.get_json() not in new_get_response.get_json()
