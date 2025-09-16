"""
This tests the staticmethod used by /payments .
"""

###################################################################################################
#  IMPORTS
###################################################################################################

import pytest
from decimal import Decimal
from src.api.v1.job_routes import JobWithPaymentsById


###################################################################################################
#  CLASSES
###################################################################################################


class DummyRank:
    def __init__(self, share):
        self.share = share

class DummyMember:
    def __init__(self, rank=None, name=""):
        self.rank = rank
        self.name = name # we use the name in the logger so need it here


###################################################################################################
#  TESTS
###################################################################################################

# calculate_member_pay takes (member, value_per_share)
# it also looks for member.rank to exist as that is required for the calculation

def test_returns_zero_when_no_member_or_rank():
    assert JobWithPaymentsById.calculate_member_pay(None, 100) == 0
    assert JobWithPaymentsById.calculate_member_pay(DummyMember(name="Alice"), 100) == 0

def test_calculates_correct_value():
    member = DummyMember(rank=DummyRank(share=3), name="Alice")
    value_per_share = 10
    result = JobWithPaymentsById.calculate_member_pay(member, value_per_share)
    assert result == 30  # 3 * 10

def test_rounds_down_decimal_values():
    member = DummyMember(rank=DummyRank(share=2), name="Alice")
    value_per_share = 10 / 3  # 6.66...
    result = JobWithPaymentsById.calculate_member_pay(member, value_per_share)
    # 2 * 3.333... = 6.666... -> should round down to 6
    assert result == 6
