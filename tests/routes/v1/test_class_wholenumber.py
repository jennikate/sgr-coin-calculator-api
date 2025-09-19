"""
Tests for the various helpers that don't fall under specific routes.
"""

## TODO: refactor tests to remove hardcoded values where possible
## TODO: refactor tests to use fixtures where possible
## TODO: review if util functions can be used to reduce code duplication

###################################################################################################
#  IMPORTS
###################################################################################################

import pytest

from marshmallow import ValidationError

from src.api.schemas import WholeNumber


###################################################################################################
#  Tests
###################################################################################################

@pytest.fixture
def field():
    return WholeNumber()


def test_accepts_integer(field):
    assert field._deserialize(42, "field", {}) == 42


def test_accepts_float_that_is_whole_number(field):
    assert field._deserialize(42.0, "field", {}) == 42


def test_rejects_float_with_decimal(field):
    with pytest.raises(ValidationError, match="Value cannot have decimals."):
        field._deserialize(42.5, "field", {})


def test_rejects_string(field):
    with pytest.raises(ValidationError, match="Value must be a whole number."):
        field._deserialize("not-a-number", "field", {})


def test_rejects_none(field):
    assert field._deserialize(None, "field", {}) is None


def test_rejects_type_error(field):
    with pytest.raises(ValidationError, match="Value must be a whole number."):
        field._deserialize([], "field", {})


###################################################################################################
#  End of file
###################################################################################################
