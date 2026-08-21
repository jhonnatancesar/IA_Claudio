"""Testes unitários da renderização do painel (TASK-081, TASK-082) —
`render_panel_page`, função pura, sem tocar o banco/FastAPI."""

from datetime import datetime, timezone

from app.observability.execution_trace import ExecutionTraceRecord
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


def _trace(
    result: str | None = "resposta pronta",
    objective: str = "buscar o clima",
    finished_at: datetime | None = datetime(2026, 8, 21, 12, 0, 5, tzinfo=timezone.utc),
) -> ExecutionTraceRecord:
    return ExecutionTraceRecord(
        execution_id="11111111-1111-1111-1111-111111111111",
        origin="app-teste",
        requester="app-teste",
        objective=objective,
        started_at=datetime(2026, 8, 21, 12, 0, 0, tzinfo=timezone.utc),
        finished_at=finished_at,
        result=result,
        step_count=1,
        tools_used=[],
        prompt_version="2026-08-16.1",
        created_at=datetime(2026, 8, 21, 12, 0, 5, tzinfo=timezone.utc),
    )


def test_render_panel_page_shows_empty_queue_message():
    html = render_panel_page([], [])

    assert "Fila vazia." in html


def test_render_panel_page_lists_queue_item_fields():
    item = _item(status=QueueItemStatus.RUNNING)

    html = render_panel_page([item], [])

    assert item.item_id in html
    assert "RUNNING" in html
    assert "2026-08-21" in html


def test_render_panel_page_never_shows_payload():
    item = _item()

    html = render_panel_page([item], [])

    assert "segredo que não deve aparecer na página" not in html


def test_render_panel_page_shows_finished_at_when_present():
    finished_at = datetime(2026, 8, 21, 12, 0, tzinfo=timezone.utc)
    item = _item(status=QueueItemStatus.COMPLETED, finished_at=finished_at)

    html = render_panel_page([item], [])

    assert finished_at.isoformat() in html


def test_render_panel_page_is_valid_minimal_html():
    html = render_panel_page([], [])

    assert html.startswith("<!doctype html>")
    assert "<title>Claudião — Painel</title>" in html
    assert "<h1>Claudião — Painel (somente leitura)</h1>" in html


def test_render_panel_page_shows_empty_executions_message():
    html = render_panel_page([], [])

    assert "Nenhuma execução registrada ainda." in html


def test_render_panel_page_lists_execution_trace_fields():
    trace = _trace()

    html = render_panel_page([], [trace])

    assert trace.execution_id in html
    assert "app-teste" in html
    assert "buscar o clima" in html
    assert "sucesso" in html
    assert "resposta pronta" in html
    assert "5.00s" in html


def test_render_panel_page_shows_failure_status_when_no_result():
    trace = _trace(result=None)

    html = render_panel_page([], [trace])

    assert "falha" in html


def test_render_panel_page_escapes_objective_and_result():
    trace = _trace(objective="<script>alert(1)</script>", result="<b>não escapado</b>")

    html = render_panel_page([], [trace])

    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html
    assert "&lt;b&gt;" in html
