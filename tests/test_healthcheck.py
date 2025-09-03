# def test_healthcheck(client):
#     resp = client.get("/health")
#     assert resp.status_code == 200
#     assert resp.json == {"status": "ok"}

# def test_example(client, db):
#     res = client.get("/")
#     assert res.status_code == 200

# def test_app_context_example(client, db, app):
#     with app.app_context():
#         res = client.get("/")
#         assert res.status_code == 200


"""
This module contains a unit test for the healthcheck endpoint resource in the `src.api.health` module.
"""


###################################################################################################
#  Tests
###################################################################################################


class TestApiHealthcheck:
    def test_app_healthcheck(self, client):
        """
        Tests that a user can retrieve a repsonse from the API.
        """
        # result = client.get("/api-healthcheck") TODO: create then change to a healthcheck endpoint
        result = client.get("/v1/ranks/")
        print("Result:", result)

        assert result.status_code == 200
        assert result.json == {"success": "API is alive"}


###################################################################################################
#  End of file.
###################################################################################################
