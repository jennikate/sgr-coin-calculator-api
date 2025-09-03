"""
Helpers for tests
"""

def assert_response_matches_models(response, models, fields=None, ignore_fields=("id",)):
    """
    Assert that a JSON API response matches the given SQLAlchemy models.

    Args:
        response: Flask test client response object
        models: list of SQLAlchemy model instances OR a single model
        fields: explicit list of fields to compare (overrides ignore_fields)
        ignore_fields: tuple of fields to ignore (default: ("id",))
    """
    data = response.get_json()

    def model_to_dict(model):
        return {
            col.name: getattr(model, col.name)
            for col in model.__table__.columns
        }

    # Convert models into list or dict
    if isinstance(models, (list, tuple)):
        expected = [model_to_dict(m) for m in models]
    else:
        expected = model_to_dict(models)

    # If fields specified, only keep those
    if fields:
        if isinstance(expected, list):
            expected = [{k: d[k] for k in fields} for d in expected]
            data = [{k: d[k] for k in fields} for d in data]
        else:
            expected = {k: expected[k] for k in fields}
            data = {k: data[k] for k in fields}
    else:
        # Otherwise strip ignored fields
        if isinstance(expected, list):
            expected = [
                {k: v for k, v in d.items() if k not in ignore_fields}
                for d in expected
            ]
            data = [
                {k: v for k, v in d.items() if k not in ignore_fields}
                for d in data
            ]
        else:
            expected = {k: v for k, v in expected.items() if k not in ignore_fields}
            data = {k: v for k, v in data.items() if k not in ignore_fields}

    assert data == expected, f"\nExpected: {expected}\nGot: {data}"

