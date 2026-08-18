"""Testes unitários da pontuação de relevância (TASK-048) — função pura,
sem tocar o banco."""

from datetime import datetime, timedelta, timezone

from app.memory.memory_model import Memory, relevance_score


def _memory(use_count: int, created_at: datetime, last_used_at=None) -> Memory:
    return Memory(
        id="00000000-0000-0000-0000-000000000000",
        owner_type="USER",
        owner_id="dono",
        content="conteúdo",
        created_at=created_at,
        use_count=use_count,
        last_used_at=last_used_at,
    )


def test_never_used_memory_uses_created_at_as_reference():
    now = datetime(2026, 8, 18, tzinfo=timezone.utc)
    memory = _memory(use_count=0, created_at=now)

    assert relevance_score(memory, now) == 0.0


def test_more_usage_increases_score_at_same_age():
    now = datetime(2026, 8, 18, tzinfo=timezone.utc)
    created_at = now - timedelta(days=1)
    less_used = _memory(use_count=1, created_at=created_at)
    more_used = _memory(use_count=5, created_at=created_at)

    assert relevance_score(more_used, now) > relevance_score(less_used, now)


def test_more_recent_last_used_increases_score():
    now = datetime(2026, 8, 18, tzinfo=timezone.utc)
    created_at = now - timedelta(days=30)
    recently_used = _memory(use_count=3, created_at=created_at, last_used_at=now - timedelta(days=1))
    long_unused = _memory(use_count=3, created_at=created_at, last_used_at=now - timedelta(days=20))

    assert relevance_score(recently_used, now) > relevance_score(long_unused, now)


def test_score_is_never_negative_even_with_future_reference():
    now = datetime(2026, 8, 18, tzinfo=timezone.utc)
    memory = _memory(use_count=3, created_at=now + timedelta(days=1))

    assert relevance_score(memory, now) >= 0.0
