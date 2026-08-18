"""Testes unitários da política de retenção (TASK-049) — só
`is_eligible_for_retention_removal`, função pura, sem tocar o banco."""

from datetime import datetime, timedelta, timezone

from app.memory.memory_model import Memory
from app.memory.retention_policy import is_eligible_for_retention_removal


def _memory(created_at: datetime, use_count: int = 0, last_used_at=None) -> Memory:
    return Memory(
        id="00000000-0000-0000-0000-000000000000",
        owner_type="USER",
        owner_id="dono",
        content="conteúdo",
        created_at=created_at,
        use_count=use_count,
        last_used_at=last_used_at,
    )


def test_old_and_unused_memory_is_eligible():
    now = datetime(2026, 8, 18, tzinfo=timezone.utc)
    memory = _memory(created_at=now - timedelta(days=200), use_count=0)

    assert is_eligible_for_retention_removal(memory, now, max_age_days=180, min_relevance=0.05) is True


def test_recent_memory_is_not_eligible_even_if_unused():
    now = datetime(2026, 8, 18, tzinfo=timezone.utc)
    memory = _memory(created_at=now - timedelta(days=5), use_count=0)

    assert is_eligible_for_retention_removal(memory, now, max_age_days=180, min_relevance=0.05) is False


def test_old_but_highly_relevant_memory_is_not_eligible():
    now = datetime(2026, 8, 18, tzinfo=timezone.utc)
    memory = _memory(
        created_at=now - timedelta(days=200), use_count=50, last_used_at=now - timedelta(days=1)
    )

    assert is_eligible_for_retention_removal(memory, now, max_age_days=180, min_relevance=0.05) is False


def test_custom_thresholds_are_respected():
    now = datetime(2026, 8, 18, tzinfo=timezone.utc)
    memory = _memory(created_at=now - timedelta(days=10), use_count=0)

    assert is_eligible_for_retention_removal(memory, now, max_age_days=5, min_relevance=0.05) is True
    assert is_eligible_for_retention_removal(memory, now, max_age_days=20, min_relevance=0.05) is False
