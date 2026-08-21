"""Teste de integração: retenção/limpeza da fila (TASK-077) contra o
PostgreSQL local. Usa a fixture `postgres_dsn`
(tests/integration/conftest.py) — pula automaticamente se o banco não
estiver disponível.
"""

from datetime import datetime, timedelta, timezone

import psycopg
import pytest

from app.queue.queue_model import (
    QueueItem,
    QueueItemStatus,
    delete_queue_item,
    get_queue_item,
    list_queue_items,
    save_queue_item,
)
from app.queue.retention_policy import apply_retention_policy


@pytest.fixture(autouse=True)
def cleanup(postgres_dsn):
    yield
    with psycopg.connect(postgres_dsn) as conn:
        conn.execute("DELETE FROM queue_items")


def _completed_item(finished_at: datetime) -> QueueItem:
    item = QueueItem.new(payload="algo")
    item.start()
    item.complete()
    item.finished_at = finished_at
    save_queue_item(item)
    return item


def test_delete_queue_item_removes_persisted_item(postgres_dsn):
    item = QueueItem.new(payload="algo")
    save_queue_item(item)

    delete_queue_item(item.item_id)

    assert get_queue_item(item.item_id) is None


def test_delete_queue_item_is_idempotent_for_unknown_id(postgres_dsn):
    delete_queue_item("00000000-0000-0000-0000-000000000000")  # não levanta


def test_apply_retention_policy_removes_old_completed_items(postgres_dsn):
    now = datetime.now(timezone.utc)
    old_item = _completed_item(finished_at=now - timedelta(days=10))

    removed = apply_retention_policy(now, max_age_days=7)

    assert removed == [old_item.item_id]
    assert get_queue_item(old_item.item_id) is None


def test_apply_retention_policy_keeps_recent_completed_items(postgres_dsn):
    now = datetime.now(timezone.utc)
    recent_item = _completed_item(finished_at=now - timedelta(days=1))

    removed = apply_retention_policy(now, max_age_days=7)

    assert removed == []
    assert get_queue_item(recent_item.item_id) is not None


def test_apply_retention_policy_never_removes_pending_items(postgres_dsn):
    old_pending = QueueItem.new(payload="algo")
    old_pending.created_at = datetime.now(timezone.utc) - timedelta(days=365)
    save_queue_item(old_pending)

    removed = apply_retention_policy(datetime.now(timezone.utc), max_age_days=7)

    assert removed == []
    assert get_queue_item(old_pending.item_id) is not None


def test_apply_retention_policy_returns_empty_when_queue_is_empty(postgres_dsn):
    assert apply_retention_policy(datetime.now(timezone.utc)) == []


def test_apply_retention_policy_only_removes_eligible_items(postgres_dsn):
    now = datetime.now(timezone.utc)
    old_item = _completed_item(finished_at=now - timedelta(days=10))
    recent_item = _completed_item(finished_at=now - timedelta(days=1))

    removed = apply_retention_policy(now, max_age_days=7)

    assert removed == [old_item.item_id]
    remaining = list_queue_items()
    assert [item.item_id for item in remaining] == [recent_item.item_id]
