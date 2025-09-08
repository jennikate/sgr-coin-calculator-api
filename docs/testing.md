# Testing

To run tests - `pytest`
with verbose output `pytest -vv`
with stdout `pytest -s`

To run coverage - `pytest --cov=src tests/`
To show coverage in terminal `pytest --cov=src --cov-report=term-missing tests/`


To run a specific test e.g.
`pytest -vv tests/routes/v1/member_rank_routes.py::TestPostMember`