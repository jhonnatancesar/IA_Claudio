"""Testes unitários da fila FIFO em memória (TASK-074): estados válidos
de `QueueItem`, transições inválidas e ordem de processamento de
`FifoQueue`.
"""

import pytest

from app.queue.queue_model import (
    FifoQueue,
    InvalidQueueItemStateError,
    QueueEmptyError,
    QueueItem,
    QueueItemStatus,
)


def test_queue_item_starts_as_pending():
    item = QueueItem.new(payload={"objective": "teste"})

    assert item.status == QueueItemStatus.PENDING
    assert item.is_terminal is False
    assert item.error is None
    assert item.finished_at is None


def test_queue_item_rejects_empty_item_id():
    with pytest.raises(ValueError):
        QueueItem(item_id="", payload=None)


def test_start_transitions_to_running():
    item = QueueItem.new(payload=None)

    item.start()

    assert item.status == QueueItemStatus.RUNNING


def test_start_twice_raises():
    item = QueueItem.new(payload=None)
    item.start()

    with pytest.raises(InvalidQueueItemStateError):
        item.start()


def test_complete_sets_finished_at():
    item = QueueItem.new(payload=None)
    item.start()

    item.complete()

    assert item.status == QueueItemStatus.COMPLETED
    assert item.finished_at is not None
    assert item.is_terminal is True


def test_complete_before_start_raises():
    item = QueueItem.new(payload=None)

    with pytest.raises(InvalidQueueItemStateError):
        item.complete()


def test_complete_twice_raises():
    item = QueueItem.new(payload=None)
    item.start()
    item.complete()

    with pytest.raises(InvalidQueueItemStateError):
        item.complete()


def test_fail_sets_error_and_finished_at():
    item = QueueItem.new(payload=None)
    item.start()

    item.fail("provedor indisponível")

    assert item.status == QueueItemStatus.FAILED
    assert item.error == "provedor indisponível"
    assert item.finished_at is not None
    assert item.is_terminal is True


def test_fail_from_pending_is_allowed():
    """Falhar antes mesmo de iniciar é válido (ex.: item rejeitado antes
    de começar a rodar)."""
    item = QueueItem.new(payload=None)

    item.fail("payload inválido")

    assert item.status == QueueItemStatus.FAILED


def test_fail_after_completed_raises():
    item = QueueItem.new(payload=None)
    item.start()
    item.complete()

    with pytest.raises(InvalidQueueItemStateError):
        item.fail("erro tardio")


def test_fail_does_not_retry():
    """Sem retry automático (seção 27) — um item FAILED não volta a
    PENDING/RUNNING sozinho."""
    item = QueueItem.new(payload=None)
    item.start()

    item.fail("erro")

    assert item.status == QueueItemStatus.FAILED
    with pytest.raises(InvalidQueueItemStateError):
        item.start()


def test_new_queue_is_empty():
    queue = FifoQueue()

    assert len(queue) == 0
    assert queue.is_empty is True


def test_enqueue_adds_pending_item():
    queue = FifoQueue()

    item = queue.enqueue(payload={"objective": "teste"})

    assert item.status == QueueItemStatus.PENDING
    assert len(queue) == 1
    assert queue.is_empty is False


def test_dequeue_returns_items_in_fifo_order():
    queue = FifoQueue()
    first = queue.enqueue(payload="primeiro")
    second = queue.enqueue(payload="segundo")

    assert queue.dequeue().item_id == first.item_id
    assert queue.dequeue().item_id == second.item_id


def test_dequeue_starts_the_item():
    queue = FifoQueue()
    queue.enqueue(payload="algo")

    item = queue.dequeue()

    assert item.status == QueueItemStatus.RUNNING


def test_dequeue_removes_item_from_queue():
    queue = FifoQueue()
    queue.enqueue(payload="algo")

    queue.dequeue()

    assert len(queue) == 0
    assert queue.is_empty is True


def test_dequeue_from_empty_queue_raises():
    queue = FifoQueue()

    with pytest.raises(QueueEmptyError):
        queue.dequeue()


def test_full_cycle_enqueue_dequeue_complete():
    queue = FifoQueue()

    enqueued = queue.enqueue(payload={"objective": "teste"})
    assert enqueued.status == QueueItemStatus.PENDING

    dequeued = queue.dequeue()
    assert dequeued.item_id == enqueued.item_id
    assert dequeued.status == QueueItemStatus.RUNNING

    dequeued.complete()
    assert dequeued.status == QueueItemStatus.COMPLETED
    assert dequeued.is_terminal is True
