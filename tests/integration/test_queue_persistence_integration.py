"""Teste de integração: persistência da fila FIFO (TASK-075) contra o
PostgreSQL local. Usa a fixture `postgres_dsn`
(tests/integration/conftest.py) — pula automaticamente se o banco não
estiver disponível.
"""

import psycopg
import pytest

from app.queue.queue_model import (
    FifoQueue,
    QueueItem,
    QueueItemStatus,
    get_queue_item,
    list_queue_items,
    save_queue_item,
)


@pytest.fixture(autouse=True)
def cleanup(postgres_dsn):
    yield
    with psycopg.connect(postgres_dsn) as conn:
        conn.execute("DELETE FROM queue_items")


def test_save_queue_item_persists_and_is_readable(postgres_dsn):
    item = QueueItem.new(payload={"objective": "buscar o clima"})

    save_queue_item(item)

    fetched = get_queue_item(item.item_id)
    assert fetched is not None
    assert fetched.item_id == item.item_id
    assert fetched.payload == {"objective": "buscar o clima"}
    assert fetched.status == QueueItemStatus.PENDING
    assert fetched.error is None
    assert fetched.finished_at is None


def test_get_queue_item_returns_none_for_unknown_id(postgres_dsn):
    assert get_queue_item("00000000-0000-0000-0000-000000000000") is None


def test_save_queue_item_updates_status_on_conflict(postgres_dsn):
    item = QueueItem.new(payload="algo")
    save_queue_item(item)

    item.start()
    save_queue_item(item)

    fetched = get_queue_item(item.item_id)
    assert fetched.status == QueueItemStatus.RUNNING


def test_save_queue_item_reflects_completion(postgres_dsn):
    item = QueueItem.new(payload="algo")
    save_queue_item(item)
    item.start()
    save_queue_item(item)

    item.complete()
    save_queue_item(item)

    fetched = get_queue_item(item.item_id)
    assert fetched.status == QueueItemStatus.COMPLETED
    assert fetched.finished_at is not None


def test_save_queue_item_reflects_failure(postgres_dsn):
    item = QueueItem.new(payload="algo")
    save_queue_item(item)
    item.start()
    save_queue_item(item)

    item.fail("provedor indisponível")
    save_queue_item(item)

    fetched = get_queue_item(item.item_id)
    assert fetched.status == QueueItemStatus.FAILED
    assert fetched.error == "provedor indisponível"
    assert fetched.finished_at is not None


def test_list_queue_items_returns_fifo_order(postgres_dsn):
    first = QueueItem.new(payload="primeiro")
    second = QueueItem.new(payload="segundo")
    save_queue_item(first)
    save_queue_item(second)

    listed = list_queue_items()

    assert [item.item_id for item in listed] == [first.item_id, second.item_id]


def test_list_queue_items_empty_when_nothing_persisted(postgres_dsn):
    assert list_queue_items() == []


def test_in_memory_queue_and_persistence_used_together(postgres_dsn):
    """Uso ponta a ponta: FifoQueue (TASK-074, em memória) continua sem
    tocar o banco sozinha — quem processa a fila chama save_queue_item
    explicitamente a cada transição."""
    queue = FifoQueue()
    enqueued = queue.enqueue(payload={"objective": "teste"})
    save_queue_item(enqueued)

    dequeued = queue.dequeue()
    save_queue_item(dequeued)

    dequeued.complete()
    save_queue_item(dequeued)

    fetched = get_queue_item(enqueued.item_id)
    assert fetched.status == QueueItemStatus.COMPLETED
