"""Suite A: the 20 age and profile boundary cases from the acceptance plan."""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "server")))

from app.main import ages_compatible, validate_registration


@pytest.mark.parametrize(
    "age_a,age_b",
    [(18, 18), (18, 19), (18, 20), (18, 21), (19, 22), (20, 23),
     (21, 18), (25, 22), (30, 27), (65, 62)],
)
def test_suite_a_compatible_pairs(age_a, age_b):
    assert ages_compatible(age_a, age_b)


@pytest.mark.parametrize(
    "age_a,age_b",
    [(18, 22), (20, 24), (25, 29), (40, 44), (65, 69)],
)
def test_suite_a_age_gap_pairs_are_refused(age_a, age_b):
    assert not ages_compatible(age_a, age_b)


@pytest.mark.parametrize(
    "payload",
    [
        {"nickname": "Teen", "birth_year": 2009},
        {"nickname": "Teen", "birth_year": 2010},
        {"nickname": "Teen", "birth_year": None},
        {"nickname": "Teen", "birth_year": "unknown"},
        {"nickname": "T", "birth_year": 2003},
    ],
)
def test_suite_a_invalid_profiles_are_rejected(payload):
    profile, error = validate_registration(payload)
    assert profile is None
    assert error and error["code"] in {"invalid_nickname", "invalid_birth_year"}
