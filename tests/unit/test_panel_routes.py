"""Testes unitários da renderização do painel (TASK-081) —
`render_panel_page`, função pura, sem tocar o banco/FastAPI."""

from datetime import datetime, timezone

from app.panel.routes import render_panel_page
from app.queue.queue_model import QueueItem, QueueItemStatus


def _item(status: QueueItemStatus = QueueItemStatus.PENDING, finished_at=None) -> QueueItem:
    return QueueItem(
        item_id="00000000-0000-0000-0000-000000000000",
        payload="segredo que não deve aparecer na página",
        status=status,
        created_at=datetime(2026, 8, 21, tzinfo=timezone.utc),
        finished_at=finished_at,
    )


def test_render_panel_page_shows_empty_queue_message():
    html = render_panel_page([])

    assert "Fila vazia." in html


def test_render_panel_page_lists_queue_item_fields():
    item = _item(status=QueueItemStatus.RUNNING)

    html = render_panel_page([item])

    assert item.item_id in html
    assert "RUNNING" in html
    assert "2026-08-21" in html


def test_render_panel_page_never_shows_payload():
    item = _item()

    html = render_panel_page([item])

    assert "segredo que não deve aparecer na página" not in html


def test_render_panel_page_shows_finished_at_when_present():
    finished_at = datetime(2026, 8, 21, 12, 0, tzinfo=timezone.utc)
    item = _item(status=QueueItemStatus.COMPLETED, finished_at=finished_at)

    html = render_panel_page([item])

    assert finished_at.isoformat() in html


def test_render_panel_page_is_valid_minimal_html():
    html = render_panel_page([])

    assert html.startswith("<!doctype html>")
    assert "<title>Claudião — Painel</title>" in html
    assert "<h1>Claudião — Painel (somente leitura)</h1>" in html
