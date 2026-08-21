"""Testes unitários da política de retenção da fila (TASK-077) — só
`is_eligible_for_retention_removal`, função pura, sem tocar o banco."""

from datetime import datetime, timedelta, timezone

from app.queue.queue_model import QueueItem, QueueItemStatus
from app.queue.retention_policy import is_eligible_for_retention_removal


def _item(status: QueueItemStatus, finished_at=None) -> QueueItem:
    return QueueItem(
        item_id="00000000-0000-0000-0000-000000000000",
        payload="algo",
        status=status,
        finished_at=finished_at,
    )


def test_old_completed_item_is_eligible():
    now = datetime(2026, 8, 21, tzinfo=timezone.utc)
    item = _item(QueueItemStatus.COMPLETED, finished_at=now - timedelta(days=10))

    assert is_eligible_for_retention_removal(item, now, max_age_days=7) is True


def test_recent_completed_item_is_not_eligible():
    now = datetime(2026, 8, 21, tzinfo=timezone.utc)
    item = _item(QueueItemStatus.COMPLETED, finished_at=now - timedelta(days=1))

    assert is_eligible_for_retention_removal(item, now, max_age_days=7) is False


def test_old_failed_item_is_eligible():
    now = datetime(2026, 8, 21, tzinfo=timezone.utc)
    item = _item(QueueItemStatus.FAILED, finished_at=now - timedelta(days=30))

    assert is_eligible_for_retention_removal(item, now, max_age_days=7) is True


def test_old_pending_item_is_never_eligible():
    """Item não-terminal nunca é elegível, mesmo muito antigo — ainda
    representa trabalho em aberto, não é limpeza de rotina."""
    now = datetime(2026, 8, 21, tzinfo=timezone.utc)
    item = _item(QueueItemStatus.PENDING, finished_at=None)

    assert is_eligible_for_retention_removal(item, now, max_age_days=7) is False


def test_old_running_item_is_never_eligible():
    now = datetime(2026, 8, 21, tzinfo=timezone.utc)
    item = _item(QueueItemStatus.RUNNING, finished_at=None)

    assert is_eligible_for_retention_removal(item, now, max_age_days=7) is False


def test_terminal_item_without_finished_at_is_not_eligible():
    """Defensivo: um item terminal sempre tem finished_at na prática
    (QueueItem.complete/fail sempre o define), mas a função não deve
    quebrar nem considerar elegível se ausente."""
    now = datetime(2026, 8, 21, tzinfo=timezone.utc)
    item = _item(QueueItemStatus.COMPLETED, finished_at=None)

    assert is_eligible_for_retention_removal(item, now, max_age_days=7) is False


def test_custom_max_age_is_respected():
    now = datetime(2026, 8, 21, tzinfo=timezone.utc)
    item = _item(QueueItemStatus.COMPLETED, finished_at=now - timedelta(days=3))

    assert is_eligible_for_retention_removal(item, now, max_age_days=1) is True
    assert is_eligible_for_retention_removal(item, now, max_age_days=5) is False
