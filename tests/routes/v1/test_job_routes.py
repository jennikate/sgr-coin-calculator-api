"""
This module contains a unit test for the job & job endpoint resource in the `src.api.v1/job_routes` module.
"""

## TODO: refactor tests to remove hardcoded values where possible
## TODO: refactor tests to use fixtures where possible
## TODO: review if util functions can be used to reduce code duplication

###################################################################################################
#  IMPORTS
###################################################################################################

import pytest

from flask import current_app

from src.api.models import JobModel # type: ignore


###################################################################################################
#  HAPPY PATHS : post, get all, get one, update, delete
###################################################################################################


class TestPostJob:
    def test_post_job(self, client):
        """
        Tests that a user can post a new job to the API.
        """
        new_job = {
            "job_name": "Ogres in Hinterlands",
            "job_description": "For Stromgarde, collecting horns for bounty",
            "start_date": "2025-04-23",
            "end_date": "2025-04-28",
            "total_silver": 100
        }
        response = client.post("/v1/job", json=new_job)
        data = response.get_json()

        expected_response = {
            "end_date": "2025-04-28",
            "id": data["id"], # UUID is generated
            "job_description": "For Stromgarde, collecting horns for bounty",
            "job_name": "Ogres in Hinterlands",
            "start_date": "2025-04-23",
            "total_silver": 100
        }

        assert response.status_code == 201
        assert data == expected_response

        # fetch the actual model from the DB
        job = JobModel.query.get(data["id"])

        expected_repr = f"""src.api.models.JobModel(company_cut_amt=None, end_date=datetime.date(2025, 4, 28), id=UUID('{data["id"]}'), job_description='For Stromgarde, collecting horns for bounty', job_name='Ogres in Hinterlands', remainder_after_payouts=None, start_date=datetime.date(2025, 4, 23), total_silver=100)"""

        assert repr(job) == expected_repr


    def test_post_job_only_required_fields(self, client):
        """
        Tests that a user can post a new job to the API.
        """
        new_job = {
            "job_name": "Ogres in Hinterlands",
            "start_date": "2025-04-23"
        }
        response = client.post("/v1/job", json=new_job)
        data = response.get_json()

        expected_response = {
            "end_date": None,
            "id": data["id"], # UUID is generated
            "job_description": None,
            "job_name": "Ogres in Hinterlands",
            "start_date": "2025-04-23",
            "total_silver": None
        }

        assert response.status_code == 201
        assert data == expected_response

        # fetch the actual model from the DB
        job = JobModel.query.get(data["id"])

        expected_repr = f"""src.api.models.JobModel(company_cut_amt=None, end_date=None, id=UUID('{data["id"]}'), job_description=None, job_name='Ogres in Hinterlands', remainder_after_payouts=None, start_date=datetime.date(2025, 4, 23), total_silver=None)"""

        assert repr(job) == expected_repr


    def test_post_job_valid_formats(self, client):
        """
        Tests that a user can post a new job to the API using non defined but still valid formats
        """
        new_job = {
            "job_name": "Ogres in Hinterlands",
            "job_description": "For Stromgarde, collecting horns for bounty",
            "start_date": "20250423", # should be converted by smorest/Marshmallow to a date
            "end_date": "20250428", # should be converted by smorest/Marshmallow to a date
            "total_silver": "100" # should be converted by smorest/Marshmallow to an int
        }
        response = client.post("/v1/job", json=new_job)
        data = response.get_json()
        print(data)

        expected_response = {
            "end_date": "2025-04-28",
            "id": data["id"], # UUID is generated
            "job_description": "For Stromgarde, collecting horns for bounty",
            "job_name": "Ogres in Hinterlands",
            "start_date": "2025-04-23",
            "total_silver": 100
        }

        assert response.status_code == 201
        assert data == expected_response

        # fetch the actual model from the DB
        job = JobModel.query.get(data["id"])

        expected_repr = f"""src.api.models.JobModel(company_cut_amt=None, end_date=datetime.date(2025, 4, 28), id=UUID('{data["id"]}'), job_description='For Stromgarde, collecting horns for bounty', job_name='Ogres in Hinterlands', remainder_after_payouts=None, start_date=datetime.date(2025, 4, 23), total_silver=100)"""

        assert repr(job) == expected_repr


class TestGetJobsWhenNoJobs:
    def test_get_all_jobs_when_none_exist(self, client):
        """
        Tests that a user can get all jobs, sorted by date.
        """
        response = client.get("/v1/jobs")
        assert response.status_code == 200
        assert response.get_json() == []

@pytest.mark.usefixtures("sample_jobs")
class TestGetJobs:
    def test_get_all_jobs(self, client, sample_jobs):
        """
        Tests that a user can get all jobs, sorted by date.
        """
        response = client.get("/v1/jobs")

        # test the response matches the sample fixtures
        # TODO: can probably loop over this instead of writing it all out
        expected_response = [
            {
                "id": str(sample_jobs[2].id),
                "job_name": str(sample_jobs[2].job_name),
                "job_description": None,
                "start_date": str(sample_jobs[2].start_date),
                "end_date": None,
                "total_silver": None,
            },
            {
                "id": str(sample_jobs[1].id),
                "job_name": str(sample_jobs[1].job_name),
                "job_description": str(sample_jobs[1].job_description),
                "start_date": str(sample_jobs[1].start_date),
                "end_date": None,
                "total_silver": int(sample_jobs[1].total_silver),
            },
            {
                "id": str(sample_jobs[0].id),
                "job_name": str(sample_jobs[0].job_name),
                "job_description": str(sample_jobs[0].job_description),
                "start_date": str(sample_jobs[0].start_date),
                "end_date": str(sample_jobs[0].end_date),
                "total_silver": int(sample_jobs[0].total_silver),
            }
        ]

        assert response.status_code == 200
        assert response.get_json() == expected_response

    def test_get_jobs_by_date(self, client, sample_jobs):
            """
            Tests that a user can get all jobs for a given date.
            """
            response = client.get("/v1/jobs?start_date=2025-04-29")
            print(f"RESPONSE -> {response.get_json()}")

            expected_response = [
                {
                    "id": str(sample_jobs[1].id),
                    "job_name": str(sample_jobs[1].job_name),
                    "job_description": str(sample_jobs[1].job_description),
                    "start_date": str(sample_jobs[1].start_date),
                    "end_date": None,
                    "total_silver": int(sample_jobs[1].total_silver),
                }
            ]

            assert response.status_code == 200
            assert response.get_json() == expected_response

    def test_get_jobs_by_date_no_jobs(self, client, sample_jobs):
            """
            Tests that a user can get all jobs for a given date.
            """
            response = client.get("/v1/jobs?start_date=2025-06-29")

            expected_response = []

            assert response.status_code == 200
            assert response.get_json() == expected_response
    
    def test_get_job_by_id(self, client, sample_jobs):
        """
        Tests that a user can get a job by id.
        """
        job_id = str(sample_jobs[0].id)
        response = client.get(f"/v1/job/{job_id}")

        expected_response = {
            "id": str(sample_jobs[0].id),
            "job_name": str(sample_jobs[0].job_name),
            "job_description": str(sample_jobs[0].job_description),
            "start_date": str(sample_jobs[0].start_date),
            "end_date": str(sample_jobs[0].end_date),
            "total_silver": int(sample_jobs[0].total_silver),
        }
        assert response.status_code == 200
        assert response.get_json() == expected_response


# TODO: extend this to various combinations of things being updated
# including from and to None values
@pytest.mark.usefixtures("sample_jobs")
class TestUpdateJob:
    def test_update_all_job_fields(self, client, sample_jobs):
        """
        Tests that a user can update a job in the API.
        """
        # Get an id to update
        id = sample_jobs[0].id 
        # Create the update details
        updated_job = {
            "job_name": "New job name",
            "job_description": "New jobs description",
            "start_date": "2026-04-23",
            "end_date": "20260428",
            "total_silver": 7
        }

        # verify details of the original job are different to the update job
        original_response = client.get(f"/v1/job/{id}")
        assert original_response != updated_job

        # update the job
        update_response = client.patch(f"/v1/job/{id}", json=updated_job)
        updated_expected_response = {
            "id": original_response.get_json()["id"], # id should remain the same
            "job_name": "New job name",
            "job_description": "New jobs description",
            "start_date": "2026-04-23",
            "end_date": "2026-04-28",
            "total_silver": 7
        }
        assert update_response.status_code == 200
        assert update_response.get_json() == updated_expected_response


@pytest.mark.usefixtures("sample_jobs")
class TestDeleteJob:
    def test_delete_job(self, client, sample_jobs):
        """
        Tests that a user can delete a job in the API.
        """
        # Get a job and verify it exists
        job_id = str(sample_jobs[0].id)
        original_response = client.get(f"/v1/job/{job_id}")

        expected_response = {
            "id": str(sample_jobs[0].id),
            "job_name": str(sample_jobs[0].job_name),
            "job_description": str(sample_jobs[0].job_description),
            "start_date": str(sample_jobs[0].start_date),
            "end_date": str(sample_jobs[0].end_date),
            "total_silver": int(sample_jobs[0].total_silver),
        }
        assert original_response.status_code == 200
        assert original_response.get_json() == expected_response

        # delete the job
        delete_response = client.delete(f"/v1/job/{job_id}")
        assert delete_response.status_code == 200
        assert delete_response.get_json() == {"message": f"job id {job_id} deleted" }

        # verify job is no longer there
        new_get_response = client.get("/v1/jobs")
        assert original_response.get_json() not in new_get_response.get_json()

###################################################################################################
#  End of file.
###################################################################################################
