"""Testes unitários do ExecutionOrchestrator (TASK-023), com um
LocalLLMProvider fake — sem depender do Ollama real. Validação contra o
Ollama de verdade está em
tests/integration/test_execution_orchestrator_integration.py."""

import json

import pytest

from app.errors.response import ClaudiaoError
from app.llm.protocol import Action, Confidence
from app.llm.provider import (
    CompletionRequest,
    CompletionResponse,
    LocalLLMProvider,
    LocalLLMProviderError,
)
from app.orchestrator.execution import Execution, ExecutionStatus
from app.orchestrator.orchestrator import ExecutionOrchestrator
from app.policies.execution_policy import ExecutionPolicy


class _ScriptedProvider(LocalLLMProvider):
    """Provider fake que devolve, em sequência, os textos configurados."""

    def __init__(self, responses: list[str] | None = None, error: Exception | None = None) -> None:
        self._responses = list(responses or [])
        self._error = error
        self.received_prompts: list[str] = []

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        self.received_prompts.append(request.prompt)
        if self._error is not None:
            raise self._error
        text = self._responses.pop(0)
        return CompletionResponse(text=text, model=request.model)

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


def _use_tool_json(execution_id: str) -> str:
    return json.dumps(
        {
            "execution_id": execution_id,
            "action": "USE_TOOL",
            "tool": "WEB_SEARCH",
            "confidence": "LOW",
            "reason": "preciso pesquisar",
            "parameters": {"query": "algo"},
        }
    )


def _orchestrator(provider: LocalLLMProvider) -> ExecutionOrchestrator:
    return ExecutionOrchestrator(provider=provider, policy=ExecutionPolicy.for_chat())


def test_run_step_starts_pending_execution():
    execution = Execution.new(origin="chat")
    provider = _ScriptedProvider([_respond_json(execution.execution_id)])

    _orchestrator(provider).run_step(execution, objective="pergunta", model="qualquer")

    assert execution.status == ExecutionStatus.COMPLETED  # RESPOND conclui


def test_run_step_with_respond_completes_execution_with_reason_as_result():
    execution = Execution.new(origin="chat")
    provider = _ScriptedProvider([_respond_json(execution.execution_id, "a resposta é 42")])

    step = _orchestrator(provider).run_step(execution, objective="pergunta", model="qualquer")

    assert step.action == Action.RESPOND
    assert execution.status == ExecutionStatus.COMPLETED
    assert execution.result == "a resposta é 42"


def test_run_step_with_use_tool_keeps_execution_running():
    execution = Execution.new(origin="chat")
    provider = _ScriptedProvider([_use_tool_json(execution.execution_id)])

    step = _orchestrator(provider).run_step(execution, objective="pergunta", model="qualquer")

    assert step.action == Action.USE_TOOL
    assert execution.status == ExecutionStatus.RUNNING
    assert execution.step_count == 1


def test_run_step_records_step_in_execution_history():
    execution = Execution.new(origin="chat")
    provider = _ScriptedProvider([_use_tool_json(execution.execution_id)])

    _orchestrator(provider).run_step(execution, objective="pergunta", model="qualquer")

    assert execution.steps[0].tool == "WEB_SEARCH"
    assert execution.steps[0].confidence == Confidence.LOW


def test_second_run_step_does_not_restart_execution():
    execution = Execution.new(origin="chat")
    provider = _ScriptedProvider(
        [_use_tool_json(execution.execution_id), _respond_json(execution.execution_id)]
    )
    orchestrator = _orchestrator(provider)

    orchestrator.run_step(execution, objective="pergunta", model="qualquer")
    orchestrator.run_step(execution, objective="pergunta", model="qualquer")

    assert execution.step_count == 2
    assert execution.status == ExecutionStatus.COMPLETED


def test_second_run_step_prompt_includes_history_of_first_step():
    execution = Execution.new(origin="chat")
    provider = _ScriptedProvider(
        [_use_tool_json(execution.execution_id), _respond_json(execution.execution_id)]
    )
    orchestrator = _orchestrator(provider)

    orchestrator.run_step(execution, objective="pergunta", model="qualquer")
    orchestrator.run_step(execution, objective="pergunta", model="qualquer")

    assert "WEB_SEARCH" in provider.received_prompts[1]


def test_run_step_marks_execution_failed_on_provider_error():
    execution = Execution.new(origin="chat")
    provider = _ScriptedProvider(error=LocalLLMProviderError("runtime indisponível"))

    with pytest.raises(LocalLLMProviderError):
        _orchestrator(provider).run_step(execution, objective="pergunta", model="qualquer")

    assert execution.status == ExecutionStatus.FAILED
    assert execution.error == "runtime indisponível"


def test_run_step_marks_execution_failed_on_invalid_protocol_response():
    execution = Execution.new(origin="chat")
    provider = _ScriptedProvider(["isso não é um JSON de protocolo válido"])

    with pytest.raises(ClaudiaoError):
        _orchestrator(provider).run_step(execution, objective="pergunta", model="qualquer")

    assert execution.status == ExecutionStatus.FAILED


def test_orchestrator_stores_provider_and_policy():
    provider = _ScriptedProvider([])
    policy = ExecutionPolicy.for_application(timeout_seconds=30.0)

    orchestrator = ExecutionOrchestrator(provider=provider, policy=policy)

    assert orchestrator.provider is provider
    assert orchestrator.policy is policy
