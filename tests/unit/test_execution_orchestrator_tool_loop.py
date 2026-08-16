"""Testes unitários de run_until_response e execução de ferramentas
(TASK-026), com provider e tool_executor fakes."""

import json

import pytest

from app.llm.protocol import ModelStep
from app.llm.provider import CompletionRequest, CompletionResponse, LocalLLMProvider
from app.orchestrator.execution import Execution, ExecutionStatus
from app.orchestrator.orchestrator import ExecutionOrchestrator, ToolExecutorNotConfiguredError
from app.policies.execution_policy import ExecutionPolicy


class _ScriptedProvider(LocalLLMProvider):
    def __init__(self, responses: list[str]) -> None:
        self._responses = list(responses)
        self.received_prompts: list[str] = []

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        self.received_prompts.append(request.prompt)
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
    return f"resultado de {step.tool}"


def _orchestrator(provider: LocalLLMProvider, tool_executor=_echo_tool_executor) -> ExecutionOrchestrator:
    return ExecutionOrchestrator(
        provider=provider,
        policy=ExecutionPolicy.for_chat(web_search_allowed=True),
        tool_executor=tool_executor,
    )


def test_run_until_response_returns_immediately_on_respond():
    execution = Execution.new(origin="chat")
    provider = _ScriptedProvider([_respond_json(execution.execution_id)])

    step = _orchestrator(provider).run_until_response(
        execution, objective="pergunta", model="qualquer"
    )

    assert step.action.value == "RESPOND"
    assert execution.status == ExecutionStatus.COMPLETED
    assert execution.step_count == 1


def test_run_until_response_executes_tool_then_responds():
    execution = Execution.new(origin="chat")
    provider = _ScriptedProvider(
        [_use_tool_json(execution.execution_id), _respond_json(execution.execution_id)]
    )

    step = _orchestrator(provider).run_until_response(
        execution, objective="pergunta", model="qualquer"
    )

    assert step.action.value == "RESPOND"
    assert execution.status == ExecutionStatus.COMPLETED
    assert execution.step_count == 2
    assert execution.observations[0] == "resultado de WEB_SEARCH"
    assert execution.observations[1] is None


def test_run_until_response_feeds_observation_back_into_next_prompt():
    execution = Execution.new(origin="chat")
    provider = _ScriptedProvider(
        [_use_tool_json(execution.execution_id), _respond_json(execution.execution_id)]
    )

    _orchestrator(provider).run_until_response(execution, objective="pergunta", model="qualquer")

    assert "resultado de WEB_SEARCH" in provider.received_prompts[1]


def test_run_until_response_executes_multiple_tool_calls():
    execution = Execution.new(origin="chat")
    provider = _ScriptedProvider(
        [
            _use_tool_json(execution.execution_id),
            _use_tool_json(execution.execution_id),
            _respond_json(execution.execution_id),
        ]
    )

    _orchestrator(provider).run_until_response(execution, objective="pergunta", model="qualquer")

    assert execution.step_count == 3
    assert execution.observations[0] == "resultado de WEB_SEARCH"
    assert execution.observations[1] == "resultado de WEB_SEARCH"


def test_run_until_response_raises_when_tool_executor_not_configured():
    execution = Execution.new(origin="chat")
    provider = _ScriptedProvider([_use_tool_json(execution.execution_id)])
    orchestrator = ExecutionOrchestrator(
        provider=provider,
        policy=ExecutionPolicy.for_chat(web_search_allowed=True),
        tool_executor=None,
    )

    with pytest.raises(ToolExecutorNotConfiguredError):
        orchestrator.run_until_response(execution, objective="pergunta", model="qualquer")

    assert execution.status == ExecutionStatus.FAILED


def test_run_until_response_fails_execution_when_tool_executor_raises():
    execution = Execution.new(origin="chat")
    provider = _ScriptedProvider([_use_tool_json(execution.execution_id)])

    def _broken_tool_executor(step: ModelStep) -> str:
        raise RuntimeError("ferramenta explodiu")

    orchestrator = _orchestrator(provider, tool_executor=_broken_tool_executor)

    with pytest.raises(RuntimeError, match="ferramenta explodiu"):
        orchestrator.run_until_response(execution, objective="pergunta", model="qualquer")

    assert execution.status == ExecutionStatus.FAILED
    assert execution.error == "ferramenta explodiu"
