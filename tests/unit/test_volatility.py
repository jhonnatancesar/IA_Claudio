"""Testes unitários de volatilidade VOLATILE/NON_VOLATILE (TASK-032)."""

import pytest

from app.confidence.volatility import Volatility, requires_revalidation


def test_volatility_has_exactly_two_values():
    assert {v.value for v in Volatility} == {"VOLATILE", "NON_VOLATILE"}


def test_volatile_requires_revalidation():
    assert requires_revalidation(Volatility.VOLATILE) is True


def test_non_volatile_does_not_require_revalidation():
    assert requires_revalidation(Volatility.NON_VOLATILE) is False


@pytest.mark.parametrize("volatility", [Volatility.VOLATILE, Volatility.NON_VOLATILE])
def test_requires_revalidation_returns_bool(volatility):
    assert isinstance(requires_revalidation(volatility), bool)
