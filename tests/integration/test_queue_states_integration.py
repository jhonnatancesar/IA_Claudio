"""Teste de integração: transições de estado da fila aplicadas direto a
um item já persistido (TASK-076), contra o PostgreSQL local. Usa a
fixture `postgres_dsn` (tests/conftest.py) — pula
automaticamente se o banco não estiver disponível.
"""

import psycopg
import pytest

from app.queue.queue_model import (
    InvalidQueueItemStateError,
    QueueItem,
    QueueItemNotFoundError,
    QueueItemStatus,
    complete_queue_item,
    fail_queue_item,
    list_queue_items_by_status,
    save_queue_item,
    start_queue_item,
)


@pytest.fixture(autouse=True)
def cleanup(postgres_dsn):
    yield
    with psycopg.connect(postgres_dsn) as conn:
        conn.execute("DELETE FROM queue_items")


def _persisted_item(payload="algo") -> QueueItem:
    item = QueueItem.new(payload=payload)
    save_queue_item(item)
    return item


def test_start_queue_item_transitions_pending_to_running(postgres_dsn):
    item = _persisted_item()

    started = start_queue_item(item.item_id)

    assert started.status == QueueItemStatus.RUNNING


def test_start_queue_item_raises_for_unknown_id(postgres_dsn):
    with pytest.raises(QueueItemNotFoundError):
        start_queue_item("00000000-0000-0000-0000-000000000000")


def test_start_queue_item_twice_raises(postgres_dsn):
    item = _persisted_item()
    start_queue_item(item.item_id)

    with pytest.raises(InvalidQueueItemStateError):
        start_queue_item(item.item_id)


def test_complete_queue_item_transitions_running_to_completed(postgres_dsn):
    item = _persisted_item()
    start_queue_item(item.item_id)

    completed = complete_queue_item(item.item_id)

    assert completed.status == QueueItemStatus.COMPLETED
    assert completed.finished_at is not None


def test_complete_queue_item_before_start_raises(postgres_dsn):
    item = _persisted_item()

    with pytest.raises(InvalidQueueItemStateError):
        complete_queue_item(item.item_id)


def test_complete_queue_item_raises_for_unknown_id(postgres_dsn):
    with pytest.raises(QueueItemNotFoundError):
        complete_queue_item("00000000-0000-0000-0000-000000000000")


def test_fail_queue_item_transitions_to_failed_with_error(postgres_dsn):
    item = _persisted_item()
    start_queue_item(item.item_id)

    failed = fail_queue_item(item.item_id, "provedor indisponível")

    assert failed.status == QueueItemStatus.FAILED
    assert failed.error == "provedor indisponível"
    assert failed.finished_at is not None


def test_fail_queue_item_from_pending_is_allowed(postgres_dsn):
    item = _persisted_item()

    failed = fail_queue_item(item.item_id, "erro de validação")

    assert failed.status == QueueItemStatus.FAILED


def test_fail_queue_item_does_not_retry(postgres_dsn):
    item = _persisted_item()
    fail_queue_item(item.item_id, "erro")

    with pytest.raises(InvalidQueueItemStateError):
        start_queue_item(item.item_id)


def test_fail_queue_item_raises_for_unknown_id(postgres_dsn):
    with pytest.raises(QueueItemNotFoundError):
        fail_queue_item("00000000-0000-0000-0000-000000000000", "erro")


def test_list_queue_items_by_status_filters_correctly(postgres_dsn):
    pending = _persisted_item("pendente")
    running = _persisted_item("rodando")
    start_queue_item(running.item_id)

    pending_items = list_queue_items_by_status(QueueItemStatus.PENDING)
    running_items = list_queue_items_by_status(QueueItemStatus.RUNNING)

    assert [i.item_id for i in pending_items] == [pending.item_id]
    assert [i.item_id for i in running_items] == [running.item_id]


def test_list_queue_items_by_status_empty_when_none_match(postgres_dsn):
    _persisted_item("pendente")

    assert list_queue_items_by_status(QueueItemStatus.COMPLETED) == []


def test_full_cycle_start_complete_by_id(postgres_dsn):
    item = _persisted_item({"objective": "teste"})

    start_queue_item(item.item_id)
    completed = complete_queue_item(item.item_id)

    assert completed.status == QueueItemStatus.COMPLETED
    assert completed.payload == {"objective": "teste"}
