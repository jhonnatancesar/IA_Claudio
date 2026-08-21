"""Teste de integração: persistência do Execution Trace (TASK-082,
DEC-010) contra o PostgreSQL local. Usa a fixture `postgres_dsn`
(tests/integration/conftest.py) — pula automaticamente se o banco não
estiver disponível.
"""

import psycopg
import pytest

from app.llm.protocol import Action, Confidence, ModelStep
from app.observability.execution_trace import (
    ExecutionTrace,
    get_execution_trace,
    list_execution_traces,
    save_execution_trace,
)


@pytest.fixture(autouse=True)
def cleanup(postgres_dsn):
    yield
    with psycopg.connect(postgres_dsn) as conn:
        conn.execute("DELETE FROM execution_traces")


def _trace(execution_id: str, objective: str = "testar") -> ExecutionTrace:
    return ExecutionTrace.new(
        execution_id=execution_id, origin="chat", requester="chat", objective=objective
    )


def test_save_execution_trace_persists_and_is_readable(postgres_dsn):
    trace = _trace("33333333-3333-3333-3333-333333333333")
    trace.add_step(
        ModelStep(
            execution_id=trace.execution_id,
            action=Action.USE_TOOL,
            confidence=Confidence.LOW,
            reason="preciso pesquisar",
            tool="WEB_SEARCH",
        )
    )
    trace.finish(result="resposta pronta")

    save_execution_trace(trace)

    fetched = get_execution_trace(trace.execution_id)
    assert fetched is not None
    assert fetched.execution_id == trace.execution_id
    assert fetched.objective == "testar"
    assert fetched.result == "resposta pronta"
    assert fetched.step_count == 1
    assert fetched.tools_used == ["WEB_SEARCH"]
    assert fetched.succeeded is True
    assert fetched.duration_seconds is not None


def test_get_execution_trace_returns_none_for_unknown_id(postgres_dsn):
    assert get_execution_trace("00000000-0000-0000-0000-000000000000") is None


def test_save_execution_trace_updates_on_conflict(postgres_dsn):
    trace = _trace("44444444-4444-4444-4444-444444444444")
    save_execution_trace(trace)

    trace.finish(result=None)
    save_execution_trace(trace)

    fetched = get_execution_trace(trace.execution_id)
    assert fetched.succeeded is False
    assert fetched.finished_at is not None


def test_list_execution_traces_returns_most_recent_first(postgres_dsn):
    first = _trace("55555555-5555-5555-5555-555555555555")
    save_execution_trace(first)
    second = _trace("66666666-6666-6666-6666-666666666666")
    save_execution_trace(second)

    listed = list_execution_traces()

    assert [t.execution_id for t in listed] == [second.execution_id, first.execution_id]


def test_list_execution_traces_respects_limit(postgres_dsn):
    for i in range(3):
        save_execution_trace(_trace(f"7777777{i}-7777-7777-7777-777777777777"))

    listed = list_execution_traces(limit=2)

    assert len(listed) == 2


def test_list_execution_traces_empty_when_none_persisted(postgres_dsn):
    assert list_execution_traces() == []
