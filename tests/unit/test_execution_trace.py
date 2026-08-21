"""Testes unitários do Execution Trace (TASK-078): criação, validação,
registro de etapas/erros e propriedades derivadas (step_count,
tools_used, duration_seconds).
"""

import pytest

from app.llm.prompt import PROMPT_VERSION
from app.llm.protocol import Action, Confidence, ModelStep
from app.observability.execution_trace import ExecutionTrace


def _step(action: Action = Action.RESPOND, tool: str | None = None) -> ModelStep:
    return ModelStep(
        execution_id="exec-1",
        action=action,
        confidence=Confidence.HIGH,
        reason="etapa de teste",
        tool=tool,
    )


def test_new_trace_has_expected_defaults():
    trace = ExecutionTrace.new(
        execution_id="exec-1", origin="chat", requester="usuario-1", objective="testar"
    )

    assert trace.execution_id == "exec-1"
    assert trace.origin == "chat"
    assert trace.requester == "usuario-1"
    assert trace.objective == "testar"
    assert trace.steps == []
    assert trace.errors == []
    assert trace.error_codes == []
    assert trace.usage is None
    assert trace.result is None
    assert trace.finished_at is None
    assert trace.prompt_version == PROMPT_VERSION
    assert trace.orchestrator_rules_version is None


def test_rejects_empty_execution_id():
    with pytest.raises(ValueError):
        ExecutionTrace.new(execution_id="", origin="chat", requester="u", objective="x")


def test_rejects_empty_origin():
    with pytest.raises(ValueError):
        ExecutionTrace.new(execution_id="exec-1", origin="  ", requester="u", objective="x")


def test_rejects_empty_requester():
    with pytest.raises(ValueError):
        ExecutionTrace.new(execution_id="exec-1", origin="chat", requester="", objective="x")


def test_step_count_reflects_steps_added():
    trace = ExecutionTrace.new(execution_id="exec-1", origin="chat", requester="u", objective="x")
    assert trace.step_count == 0

    trace.add_step(_step())
    trace.add_step(_step())

    assert trace.step_count == 2
    assert len(trace.steps) == 2


def test_tools_used_lists_tools_from_steps_in_order():
    trace = ExecutionTrace.new(execution_id="exec-1", origin="chat", requester="u", objective="x")
    trace.add_step(_step(action=Action.USE_TOOL, tool="WEB_SEARCH"))
    trace.add_step(_step(action=Action.USE_TOOL, tool="MEMORY"))
    trace.add_step(_step(action=Action.RESPOND))

    assert trace.tools_used == ["WEB_SEARCH", "MEMORY"]


def test_tools_used_allows_repeated_tools():
    trace = ExecutionTrace.new(execution_id="exec-1", origin="chat", requester="u", objective="x")
    trace.add_step(_step(action=Action.USE_TOOL, tool="WEB_SEARCH"))
    trace.add_step(_step(action=Action.USE_TOOL, tool="WEB_SEARCH"))

    assert trace.tools_used == ["WEB_SEARCH", "WEB_SEARCH"]


def test_tools_used_empty_when_no_tool_steps():
    trace = ExecutionTrace.new(execution_id="exec-1", origin="chat", requester="u", objective="x")
    trace.add_step(_step(action=Action.RESPOND))

    assert trace.tools_used == []


def test_record_error_appends_error_and_code():
    trace = ExecutionTrace.new(execution_id="exec-1", origin="chat", requester="u", objective="x")

    trace.record_error("falha ao chamar o modelo", code=3002)

    assert trace.errors == ["falha ao chamar o modelo"]
    assert trace.error_codes == [3002]


def test_record_error_without_code_does_not_append_to_error_codes():
    trace = ExecutionTrace.new(execution_id="exec-1", origin="chat", requester="u", objective="x")

    trace.record_error("erro sem código")

    assert trace.errors == ["erro sem código"]
    assert trace.error_codes == []


def test_record_error_can_be_called_multiple_times():
    trace = ExecutionTrace.new(execution_id="exec-1", origin="chat", requester="u", objective="x")

    trace.record_error("primeiro erro", code=1001)
    trace.record_error("segundo erro", code=1002)

    assert trace.errors == ["primeiro erro", "segundo erro"]
    assert trace.error_codes == [1001, 1002]


def test_duration_seconds_is_none_before_finish():
    trace = ExecutionTrace.new(execution_id="exec-1", origin="chat", requester="u", objective="x")

    assert trace.duration_seconds is None


def test_finish_sets_finished_at_and_result():
    trace = ExecutionTrace.new(execution_id="exec-1", origin="chat", requester="u", objective="x")

    trace.finish(result="resposta final")

    assert trace.finished_at is not None
    assert trace.result == "resposta final"


def test_duration_seconds_is_non_negative_after_finish():
    trace = ExecutionTrace.new(execution_id="exec-1", origin="chat", requester="u", objective="x")

    trace.finish(result="resposta final")

    assert trace.duration_seconds is not None
    assert trace.duration_seconds >= 0


def test_finish_accepts_no_result_for_failed_executions():
    trace = ExecutionTrace.new(execution_id="exec-1", origin="chat", requester="u", objective="x")

    trace.record_error("provedor indisponível", code=3002)
    trace.finish(result=None)

    assert trace.finished_at is not None
    assert trace.result is None
    assert trace.errors == ["provedor indisponível"]


def test_full_cycle_new_add_steps_record_error_finish():
    trace = ExecutionTrace.new(
        execution_id="exec-full", origin="application", requester="app-1", objective="buscar algo"
    )

    trace.add_step(_step(action=Action.USE_TOOL, tool="WEB_SEARCH"))
    trace.add_step(_step(action=Action.RESPOND))
    trace.finish(result="resposta pronta")

    assert trace.step_count == 2
    assert trace.tools_used == ["WEB_SEARCH"]
    assert trace.result == "resposta pronta"
    assert trace.duration_seconds is not None
    assert trace.errors == []
