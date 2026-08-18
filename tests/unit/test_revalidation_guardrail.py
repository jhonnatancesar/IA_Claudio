"""Testes unitários da regra obrigatória para informação volátil (TASK-035)."""

import pytest

from app.confidence.revalidation_guardrail import (
    VOLATILE_INFORMATION_NOT_REVALIDATED,
    ensure_volatile_information_revalidated,
)
from app.confidence.volatility import Volatility
from app.errors.response import ClaudiaoError


def test_volatile_information_not_revalidated_is_blocked():
    with pytest.raises(ClaudiaoError) as exc_info:
        ensure_volatile_information_revalidated(Volatility.VOLATILE, was_revalidated=False)

    assert exc_info.value.definition == VOLATILE_INFORMATION_NOT_REVALIDATED
    assert exc_info.value.details == {"volatility": "VOLATILE"}


def test_volatile_information_revalidated_is_allowed():
    ensure_volatile_information_revalidated(Volatility.VOLATILE, was_revalidated=True)


@pytest.mark.parametrize("was_revalidated", [True, False])
def test_non_volatile_information_is_always_allowed(was_revalidated):
    ensure_volatile_information_revalidated(
        Volatility.NON_VOLATILE, was_revalidated=was_revalidated
    )
