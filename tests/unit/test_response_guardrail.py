"""Testes unitários do bloqueio de resposta conclusiva em LOW (TASK-034)."""

import pytest

from app.confidence.response_guardrail import (
    LOW_CONFIDENCE_BLOCKED,
    ensure_conclusive_response_allowed,
)
from app.errors.response import ClaudiaoError
from app.llm.protocol import Confidence


def test_low_confidence_is_blocked():
    with pytest.raises(ClaudiaoError) as exc_info:
        ensure_conclusive_response_allowed(Confidence.LOW)

    assert exc_info.value.definition == LOW_CONFIDENCE_BLOCKED
    assert exc_info.value.details == {"final_confidence": "LOW"}


@pytest.mark.parametrize("confidence", [Confidence.MEDIUM, Confidence.HIGH])
def test_medium_and_high_confidence_are_allowed(confidence):
    ensure_conclusive_response_allowed(confidence)
