# Testing

To run tests - `pytest`
with verbose output `pytest -vv`
with stdout `pytest -s`

To run coverage - `pytest --cov=src tests/`
To show coverage in terminal `pytest --cov=src --cov-report=term-missing tests/`


To run a specific test e.g.
`pytest -vv tests/routes/v1/member_rank_routes.py::TestPostMember`


To manually test with Insomnia
Base queries are created in docs/Insomnia_2025-09-19.yaml.
You can import them to Insomnia v5 and work from there