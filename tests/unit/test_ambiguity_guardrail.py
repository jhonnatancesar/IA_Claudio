"""Testes unitários do tratamento de ambiguidade (TASK-036)."""

import pytest

from app.confidence.ambiguity_guardrail import (
    UNRESOLVED_AMBIGUITY,
    ensure_ambiguity_resolved_before_response,
)
from app.errors.response import ClaudiaoError


def test_ambiguous_without_clarification_is_blocked():
    with pytest.raises(ClaudiaoError) as exc_info:
        ensure_ambiguity_resolved_before_response(
            is_ambiguous=True, clarification_requested=False
        )

    assert exc_info.value.definition == UNRESOLVED_AMBIGUITY


def test_ambiguous_with_clarification_is_allowed():
    ensure_ambiguity_resolved_before_response(
        is_ambiguous=True, clarification_requested=True
    )


@pytest.mark.parametrize("clarification_requested", [True, False])
def test_non_ambiguous_is_always_allowed(clarification_requested):
    ensure_ambiguity_resolved_before_response(
        is_ambiguous=False, clarification_requested=clarification_requested
    )
