"""Teste de integração: política de retenção (TASK-049) removendo de
verdade no PostgreSQL local. Usa a fixture `postgres_dsn`
(tests/integration/conftest.py) — pula automaticamente se o banco não
estiver disponível.
"""

import uuid
from datetime import datetime, timedelta, timezone

import psycopg
import pytest

from app.memory.memory_model import get_memory, save_memory
from app.memory.retention_policy import apply_retention_policy


@pytest.fixture
def unique_owner_id(postgres_dsn):
    owner_id = f"teste_task049_{uuid.uuid4().hex[:12]}"
    yield owner_id
    with psycopg.connect(postgres_dsn) as conn:
        conn.execute("DELETE FROM memories WHERE owner_id = %s", (owner_id,))


def _backdate(postgres_dsn, memory_id, days: int) -> None:
    with psycopg.connect(postgres_dsn) as conn:
        conn.execute(
            "UPDATE memories SET created_at = created_at - %s * interval '1 day' "
            "WHERE id = %s",
            (days, memory_id),
        )


def test_apply_retention_policy_removes_old_unused_memory(postgres_dsn, unique_owner_id):
    memory = save_memory("USER", unique_owner_id, "memória antiga e não usada")
    _backdate(postgres_dsn, memory.id, 200)
    now = datetime.now(timezone.utc)

    removed = apply_retention_policy(
        "USER", unique_owner_id, now, max_age_days=180, min_relevance=0.05
    )

    assert removed == [memory.id]
    assert get_memory(memory.id) is None


def test_apply_retention_policy_keeps_recent_memory(postgres_dsn, unique_owner_id):
    memory = save_memory("USER", unique_owner_id, "memória recente")
    now = datetime.now(timezone.utc)

    removed = apply_retention_policy(
        "USER", unique_owner_id, now, max_age_days=180, min_relevance=0.05
    )

    assert removed == []
    assert get_memory(memory.id) is not None


def test_apply_retention_policy_does_not_touch_other_owner(postgres_dsn, unique_owner_id):
    other_owner_id = f"{unique_owner_id}_outro"
    memory = save_memory("USER", other_owner_id, "memória de outro dono")
    _backdate(postgres_dsn, memory.id, 200)
    now = datetime.now(timezone.utc)

    try:
        removed = apply_retention_policy(
            "USER", unique_owner_id, now, max_age_days=180, min_relevance=0.05
        )

        assert removed == []
        assert get_memory(memory.id) is not None
    finally:
        with psycopg.connect(postgres_dsn) as conn:
            conn.execute("DELETE FROM memories WHERE owner_id = %s", (other_owner_id,))
