"""Testes unitários da regra de bloqueio automático (TASK-065) — só
`is_eligible_for_auto_block`, função pura, sem tocar o banco."""

import pytest

from app.sources.auto_block_rule import is_eligible_for_auto_block
from app.sources.source_registry import SourceReputation


@pytest.mark.parametrize(
    "reputation,expected",
    [
        (SourceReputation.LOW, True),
        (SourceReputation.MEDIUM, False),
        (SourceReputation.HIGH, False),
    ],
)
def test_is_eligible_for_auto_block(reputation, expected):
    assert is_eligible_for_auto_block(reputation) is expected
