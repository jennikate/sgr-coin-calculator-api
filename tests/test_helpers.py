"""
This contains helper functions that can be used across the test files.
"""

# TODO: refactor so this works for calling any endpoint
# and update test files to use it for all api calls

###################################################################################################
#  IMPORTS
###################################################################################################


from src import db


###################################################################################################
#  HELPERS
###################################################################################################

def assert_job_update(client, expected_response, job_id, updated_job, expected_status = 200):
    """
    Reusable helper to assert that updating a job works as expected.
    """
    # Get the original job
    original_response = client.get(f"/v1/job/{job_id}")
    original_data = original_response.get_json()

    # Verify that the update actually changes something
    assert original_data != updated_job

    # Perform the update
    update_response = client.patch(f"/v1/job/{job_id}", json=updated_job)

    # Assert status code and response
    assert update_response.status_code == expected_status
    assert update_response.get_json() == expected_response