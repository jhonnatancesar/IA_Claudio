"""Testes unitários da regra de atualização de reputação (TASK-062) — só
`update_reputation`, função pura, sem tocar o banco."""

import pytest

from app.sources.reputation_rule import update_reputation
from app.sources.source_registry import SourceReputation


@pytest.mark.parametrize(
    "current,expected",
    [
        (SourceReputation.HIGH, SourceReputation.MEDIUM),
        (SourceReputation.MEDIUM, SourceReputation.LOW),
        (SourceReputation.LOW, SourceReputation.LOW),
    ],
)
def test_inaccurate_result_steps_down(current, expected):
    assert update_reputation(current, was_accurate=False) == expected


@pytest.mark.parametrize(
    "current,expected",
    [
        (SourceReputation.LOW, SourceReputation.MEDIUM),
        (SourceReputation.MEDIUM, SourceReputation.HIGH),
        (SourceReputation.HIGH, SourceReputation.HIGH),
    ],
)
def test_accurate_result_steps_up(current, expected):
    assert update_reputation(current, was_accurate=True) == expected
