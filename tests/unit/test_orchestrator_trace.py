"""Testes unitários da conexão do Execution Trace ao ExecutionOrchestrator
(TASK-079): `run_step`/`run_until_response` registrando etapas e tempos
num `ExecutionTrace`, com provider/tool_executor fakes."""

import json
import time

import pytest

from app.llm.protocol import ModelStep
from app.llm.provider import CompletionRequest, CompletionResponse, LocalLLMProvider
from app.observability.execution_trace import ExecutionTrace
from app.orchestrator.execution import Execution
from app.orchestrator.orchestrator import ExecutionOrchestrator, ToolExecutorNotConfiguredError
from app.policies.execution_policy import ExecutionPolicy


class _ScriptedProvider(LocalLLMProvider):
    def __init__(self, responses: list[str], delay_seconds: float = 0.0) -> None:
        self._responses = list(responses)
        self._delay_seconds = delay_seconds

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        if self._delay_seconds:
            time.sleep(self._delay_seconds)
        return CompletionResponse(text=self._responses.pop(0), model=request.model)

    def is_available(self) -> bool:
        return True


def _respond_json(execution_id: str, reason: str = "resposta pronta") -> str:
    return json.dumps(
        {
            "execution_id": execution_id,
            "action": "RESPOND",
            "confidence": "HIGH",
            "reason": reason,
        }
    )


def _use_tool_json(execution_id: str, tool: str = "WEB_SEARCH") -> str:
    return json.dumps(
        {
            "execution_id": execution_id,
            "action": "USE_TOOL",
            "tool": tool,
            "confidence": "LOW",
            "reason": "preciso pesquisar",
            "parameters": {"query": "algo"},
        }
    )


def _echo_tool_executor(step: ModelStep) -> str:
    if step.tool == "SLOW_TOOL":
        time.sleep(0.02)
    return f"resultado de {step.tool}"


def _orchestrator(provider: LocalLLMProvider, tool_executor=_echo_tool_executor) -> ExecutionOrchestrator:
    return ExecutionOrchestrator(
        provider=provider,
        policy=ExecutionPolicy.for_chat(web_search_allowed=True),
        tool_executor=tool_executor,
    )


def _trace(execution: Execution, objective: str = "pergunta") -> ExecutionTrace:
    return ExecutionTrace.new(
        execution_id=execution.execution_id, origin="chat", requester="chat", objective=objective
    )


def test_run_step_without_trace_does_not_raise():
    """`trace=None` (padrão) não muda nada do comportamento já existente."""
    execution = Execution.new(origin="chat")
    provider = _ScriptedProvider([_respond_json(execution.execution_id)])

    step = _orchestrator(provider).run_step(execution, objective="pergunta", model="qualquer")

    assert step.action.value == "RESPOND"


def test_run_step_records_step_in_trace():
    execution = Execution.new(origin="chat")
    provider = _ScriptedProvider([_respond_json(execution.execution_id)])
    trace = _trace(execution)

    _orchestrator(provider).run_step(execution, objective="pergunta", model="qualquer", trace=trace)

    assert trace.step_count == 1
    assert trace.steps[0].action.value == "RESPOND"


def test_run_step_records_call_duration():
    execution = Execution.new(origin="chat")
    provider = _ScriptedProvider([_respond_json(execution.execution_id)], delay_seconds=0.02)
    trace = _trace(execution)

    _orchestrator(provider).run_step(execution, objective="pergunta", model="qualquer", trace=trace)

    assert len(trace.step_durations) == 1
    assert trace.step_durations[0] >= 0.02


def test_run_step_does_not_record_invalid_step_in_trace():
    """Uma resposta do modelo fora do protocolo não vira etapa registrada
    em `execution` nem em `trace` — só `execution.fail()` acontece."""
    execution = Execution.new(origin="chat")
    provider = _ScriptedProvider(["isso não é JSON válido"])
    trace = _trace(execution)

    with pytest.raises(Exception):
        _orchestrator(provider).run_step(
            execution, objective="pergunta", model="qualquer", trace=trace
        )

    assert trace.step_count == 0
    assert trace.step_durations == []


def test_run_until_response_records_tools_used_and_tool_durations():
    execution = Execution.new(origin="chat")
    provider = _ScriptedProvider(
        [_use_tool_json(execution.execution_id), _respond_json(execution.execution_id)]
    )
    trace = _trace(execution)

    _orchestrator(provider).run_until_response(
        execution, objective="pergunta", model="qualquer", trace=trace
    )

    assert trace.step_count == 2
    assert trace.tools_used == ["WEB_SEARCH"]
    assert len(trace.tool_durations) == 1


def test_run_until_response_tool_durations_aligned_with_tools_used():
    execution = Execution.new(origin="chat")
    provider = _ScriptedProvider(
        [
            _use_tool_json(execution.execution_id, tool="FAST_TOOL"),
            _use_tool_json(execution.execution_id, tool="SLOW_TOOL"),
            _respond_json(execution.execution_id),
        ]
    )
    trace = _trace(execution)

    _orchestrator(provider).run_until_response(
        execution, objective="pergunta", model="qualquer", trace=trace
    )

    assert trace.tools_used == ["FAST_TOOL", "SLOW_TOOL"]
    assert len(trace.tool_durations) == 2
    # SLOW_TOOL dorme 0.02s a mais que FAST_TOOL — o índice 1 (alinhado com
    # tools_used[1] == "SLOW_TOOL") deve refletir isso.
    assert trace.tool_durations[1] >= 0.02


def test_run_until_response_does_not_record_tool_duration_on_respond_only():
    execution = Execution.new(origin="chat")
    provider = _ScriptedProvider([_respond_json(execution.execution_id)])
    trace = _trace(execution)

    _orchestrator(provider).run_until_response(
        execution, objective="pergunta", model="qualquer", trace=trace
    )

    assert trace.tools_used == []
    assert trace.tool_durations == []


def test_run_until_response_does_not_record_tool_duration_when_tool_executor_missing():
    execution = Execution.new(origin="chat")
    provider = _ScriptedProvider([_use_tool_json(execution.execution_id)])
    orchestrator = ExecutionOrchestrator(
        provider=provider,
        policy=ExecutionPolicy.for_chat(web_search_allowed=True),
        tool_executor=None,
    )
    trace = _trace(execution)

    with pytest.raises(ToolExecutorNotConfiguredError):
        orchestrator.run_until_response(
            execution, objective="pergunta", model="qualquer", trace=trace
        )

    assert trace.step_count == 1
    assert trace.tool_durations == []


def test_run_until_response_without_trace_still_works():
    execution = Execution.new(origin="chat")
    provider = _ScriptedProvider(
        [_use_tool_json(execution.execution_id), _respond_json(execution.execution_id)]
    )

    step = _orchestrator(provider).run_until_response(
        execution, objective="pergunta", model="qualquer"
    )

    assert step.action.value == "RESPOND"
