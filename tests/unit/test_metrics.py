"""Testes unitários das métricas básicas (TASK-080) — funções puras,
sem tocar rede/banco."""

from datetime import datetime, timezone
from uuid import uuid4

from app.observability.execution_trace import ExecutionTrace
from app.observability.metrics import (
    average_duration_seconds,
    average_step_count,
    failure_counts_by_error_code,
    request_count_by_status,
    success_rate,
    tool_usage_counts,
)
from app.usage.usage_model import UsageRecord
from app.llm.protocol import Action, Confidence, ModelStep


def _trace(execution_id: str = "exec-1") -> ExecutionTrace:
    return ExecutionTrace.new(
        execution_id=execution_id, origin="chat", requester="chat", objective="testar"
    )


def _step(action: Action = Action.RESPOND, tool: str | None = None) -> ModelStep:
    return ModelStep(
        execution_id="exec-1",
        action=action,
        confidence=Confidence.HIGH,
        reason="etapa",
        tool=tool,
    )


def _usage_record(status: str) -> UsageRecord:
    return UsageRecord(
        id=uuid4(),
        application_id=uuid4(),
        execution_id=str(uuid4()),
        status=status,
        created_at=datetime.now(timezone.utc),
    )


# success_rate


def test_success_rate_is_none_for_empty_list():
    assert success_rate([]) is None


def test_success_rate_all_succeeded():
    traces = [_trace(), _trace()]
    for trace in traces:
        trace.finish(result="resposta pronta")

    assert success_rate(traces) == 1.0


def test_success_rate_all_failed():
    traces = [_trace(), _trace()]
    for trace in traces:
        trace.finish(result=None)

    assert success_rate(traces) == 0.0


def test_success_rate_mixed():
    succeeded = _trace()
    succeeded.finish(result="ok")
    failed = _trace()
    failed.finish(result=None)

    assert success_rate([succeeded, failed]) == 0.5


# average_step_count


def test_average_step_count_is_none_for_empty_list():
    assert average_step_count([]) is None


def test_average_step_count_computes_mean():
    trace_a = _trace()
    trace_a.add_step(_step())
    trace_b = _trace()
    trace_b.add_step(_step())
    trace_b.add_step(_step())

    assert average_step_count([trace_a, trace_b]) == 1.5


# average_duration_seconds


def test_average_duration_seconds_is_none_when_none_finished():
    traces = [_trace(), _trace()]

    assert average_duration_seconds(traces) is None


def test_average_duration_seconds_only_counts_finished_traces():
    finished = _trace()
    finished.finish(result="ok")
    unfinished = _trace()

    result = average_duration_seconds([finished, unfinished])

    assert result is not None
    assert result >= 0


# tool_usage_counts


def test_tool_usage_counts_empty_when_no_tools_used():
    trace = _trace()
    trace.add_step(_step(action=Action.RESPOND))

    assert tool_usage_counts([trace]) == {}


def test_tool_usage_counts_aggregates_across_traces():
    trace_a = _trace()
    trace_a.add_step(_step(action=Action.USE_TOOL, tool="WEB_SEARCH"))
    trace_b = _trace()
    trace_b.add_step(_step(action=Action.USE_TOOL, tool="WEB_SEARCH"))
    trace_b.add_step(_step(action=Action.USE_TOOL, tool="MEMORY"))

    assert tool_usage_counts([trace_a, trace_b]) == {"WEB_SEARCH": 2, "MEMORY": 1}


# failure_counts_by_error_code


def test_failure_counts_by_error_code_empty_when_no_errors_recorded():
    trace = _trace()

    assert failure_counts_by_error_code([trace]) == {}


def test_failure_counts_by_error_code_aggregates_across_traces():
    trace_a = _trace()
    trace_a.record_error("falha ao chamar o modelo", code=3002)
    trace_b = _trace()
    trace_b.record_error("outra falha", code=3002)
    trace_b.record_error("json inválido", code=4001)

    assert failure_counts_by_error_code([trace_a, trace_b]) == {3002: 2, 4001: 1}


# request_count_by_status


def test_request_count_by_status_empty_for_no_records():
    assert request_count_by_status([]) == {}


def test_request_count_by_status_aggregates_by_status():
    records = [
        _usage_record("COMPLETED"),
        _usage_record("COMPLETED"),
        _usage_record("FAILED"),
    ]

    assert request_count_by_status(records) == {"COMPLETED": 2, "FAILED": 1}
