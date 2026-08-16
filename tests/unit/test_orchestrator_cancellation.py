"""Testes unitários do cancelamento integrado ao ExecutionOrchestrator
(TASK-030), com provider e tool_executor fakes."""

import json

import pytest

from app.llm.provider import CompletionRequest, CompletionResponse, LocalLLMProvider
from app.orchestrator.cancellation import CancellationToken, ExecutionCancelledError
from app.orchestrator.execution import Execution, ExecutionStatus
from app.orchestrator.orchestrator import ExecutionOrchestrator
from app.orchestrator.planner import plan_initial_step
from app.orchestrator.replanner import CannotReplanFinishedExecutionError, replan
from app.policies.execution_policy import ExecutionPolicy


class _CountingProvider(LocalLLMProvider):
    def __init__(self, execution_id: str) -> None:
        self._execution_id = execution_id
        self.calls = 0

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        self.calls += 1
        return CompletionResponse(
            text=json.dumps(
                {
                    "execution_id": self._execution_id,
                    "action": "USE_TOOL",
                    "tool": "WEB_SEARCH",
                    "confidence": "LOW",
                    "reason": "preciso pesquisar",
                    "parameters": {"query": f"consulta {self.calls}"},
                }
            ),
            model=request.model,
        )

    def is_available(self) -> bool:
        return True


def test_run_step_raises_immediately_when_token_already_cancelled():
    execution = Execution.new(origin="chat")
    provider = _CountingProvider(execution.execution_id)
    orchestrator = ExecutionOrchestrator(
        provider=provider, policy=ExecutionPolicy.for_chat(web_search_allowed=True)
    )
    token = CancellationToken()
    token.cancel("usuário cancelou")

    with pytest.raises(ExecutionCancelledError):
        orchestrator.run_step(execution, objective="pergunta", model="qualquer", cancellation_token=token)

    assert execution.status == ExecutionStatus.CANCELLED
    assert execution.error == "usuário cancelou"
    assert provider.calls == 0  # não chegou a chamar o modelo


def test_run_until_response_stops_when_cancelled_mid_loop():
    execution = Execution.new(origin="chat")
    provider = _CountingProvider(execution.execution_id)
    orchestrator = ExecutionOrchestrator(
        provider=provider,
        policy=ExecutionPolicy.for_chat(web_search_allowed=True, max_steps=10),
        tool_executor=lambda step: "resultado",
        loop_repeat_threshold=10,  # não deixa a detecção de loop interferir
    )
    token = CancellationToken()

    def _tool_executor_that_cancels(step):
        token.cancel("cancelado depois da primeira ferramenta")
        return "resultado"

    orchestrator.tool_executor = _tool_executor_that_cancels

    with pytest.raises(ExecutionCancelledError):
        orchestrator.run_until_response(
            execution, objective="pergunta", model="qualquer", cancellation_token=token
        )

    assert execution.status == ExecutionStatus.CANCELLED
    assert execution.step_count == 1  # só a primeira etapa foi registrada
    assert provider.calls == 1  # segunda chamada ao modelo nunca aconteceu


def test_plan_initial_step_forwards_cancellation_token():
    execution = Execution.new(origin="chat")
    provider = _CountingProvider(execution.execution_id)
    orchestrator = ExecutionOrchestrator(
        provider=provider, policy=ExecutionPolicy.for_chat(web_search_allowed=True)
    )
    token = CancellationToken()
    token.cancel()

    with pytest.raises(ExecutionCancelledError):
        plan_initial_step(orchestrator, execution, objective="pergunta", model="qualquer", cancellation_token=token)

    assert execution.status == ExecutionStatus.CANCELLED
    assert provider.calls == 0


def test_replan_rejects_already_cancelled_execution():
    execution = Execution.new(origin="chat")
    execution.cancel("cancelado antes")
    orchestrator = ExecutionOrchestrator(
        provider=_CountingProvider(execution.execution_id),
        policy=ExecutionPolicy.for_chat(web_search_allowed=True),
    )

    with pytest.raises(CannotReplanFinishedExecutionError):
        replan(orchestrator, execution, objective="outra pergunta", model="qualquer")
