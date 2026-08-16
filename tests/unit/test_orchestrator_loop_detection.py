"""Testes unitários da detecção de loop integrada ao ExecutionOrchestrator
(TASK-029), com provider e tool_executor fakes."""

import json

import pytest

from app.errors.response import ClaudiaoError
from app.llm.provider import CompletionRequest, CompletionResponse, LocalLLMProvider
from app.orchestrator.execution import Execution, ExecutionStatus
from app.orchestrator.loop_detector import LOOP_DETECTED
from app.orchestrator.orchestrator import ExecutionOrchestrator
from app.policies.execution_policy import ExecutionPolicy


class _RepeatingToolProvider(LocalLLMProvider):
    """Sempre pede a mesma ferramenta com os mesmos parâmetros."""

    def __init__(self, execution_id: str) -> None:
        self._execution_id = execution_id

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        return CompletionResponse(
            text=json.dumps(
                {
                    "execution_id": self._execution_id,
                    "action": "USE_TOOL",
                    "tool": "WEB_SEARCH",
                    "confidence": "LOW",
                    "reason": "preciso pesquisar",
                    "parameters": {"query": "sempre a mesma"},
                }
            ),
            model=request.model,
        )

    def is_available(self) -> bool:
        return True


class _ProgressingToolProvider(LocalLLMProvider):
    """Pede a mesma ferramenta, mas com parâmetros diferentes a cada vez —
    não deve disparar detecção de loop, mesmo repetindo a ferramenta."""

    def __init__(self, execution_id: str) -> None:
        self._execution_id = execution_id
        self._count = 0

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        self._count += 1
        return CompletionResponse(
            text=json.dumps(
                {
                    "execution_id": self._execution_id,
                    "action": "USE_TOOL",
                    "tool": "WEB_SEARCH",
                    "confidence": "LOW",
                    "reason": "preciso pesquisar mais",
                    "parameters": {"query": f"consulta {self._count}"},
                }
            ),
            model=request.model,
        )

    def is_available(self) -> bool:
        return True


def test_run_until_response_stops_on_detected_loop():
    execution = Execution.new(origin="chat")
    orchestrator = ExecutionOrchestrator(
        provider=_RepeatingToolProvider(execution.execution_id),
        policy=ExecutionPolicy.for_chat(web_search_allowed=True, max_steps=10),
        tool_executor=lambda step: "resultado",
        loop_repeat_threshold=3,
    )

    with pytest.raises(ClaudiaoError) as exc_info:
        orchestrator.run_until_response(execution, objective="pergunta", model="qualquer")

    assert exc_info.value.definition is LOOP_DETECTED
    assert execution.status == ExecutionStatus.FAILED
    assert execution.step_count == 3  # parou assim que o loop foi detectado, antes de max_steps


def test_run_until_response_does_not_flag_progressing_tool_calls_as_loop():
    execution = Execution.new(origin="chat")
    orchestrator = ExecutionOrchestrator(
        provider=_ProgressingToolProvider(execution.execution_id),
        policy=ExecutionPolicy.for_chat(web_search_allowed=True, max_steps=5),
        tool_executor=lambda step: "resultado",
        loop_repeat_threshold=3,
    )

    with pytest.raises(ClaudiaoError) as exc_info:
        orchestrator.run_until_response(execution, objective="pergunta", model="qualquer")

    # não foi detecção de loop — foi max_steps, porque os parâmetros mudam a
    # cada chamada (progresso real, não repetição).
    from app.orchestrator.orchestrator import MAX_STEPS_EXCEEDED

    assert exc_info.value.definition is MAX_STEPS_EXCEEDED
    assert execution.step_count == 5


def test_default_loop_repeat_threshold_is_three():
    orchestrator = ExecutionOrchestrator(
        provider=_RepeatingToolProvider("qualquer"),
        policy=ExecutionPolicy.for_chat(web_search_allowed=True),
    )

    assert orchestrator.loop_repeat_threshold == 3
