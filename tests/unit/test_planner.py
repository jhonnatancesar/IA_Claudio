"""Testes unitários do planejamento inicial (TASK-024), com provider fake."""

import json

import pytest

from app.llm.protocol import Action
from app.llm.provider import CompletionRequest, CompletionResponse, LocalLLMProvider
from app.orchestrator.execution import Execution, ExecutionStatus
from app.orchestrator.orchestrator import ExecutionOrchestrator
from app.orchestrator.planner import ExecutionAlreadyPlannedError, plan_initial_step
from app.policies.execution_policy import ExecutionPolicy


class _ScriptedProvider(LocalLLMProvider):
    def __init__(self, responses: list[str]) -> None:
        self._responses = list(responses)

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        return CompletionResponse(text=self._responses.pop(0), model=request.model)

    def is_available(self) -> bool:
        return True


def _respond_json(execution_id: str) -> str:
    return json.dumps(
        {
            "execution_id": execution_id,
            "action": "RESPOND",
            "confidence": "HIGH",
            "reason": "já sei a resposta",
        }
    )


def _orchestrator(provider: LocalLLMProvider) -> ExecutionOrchestrator:
    return ExecutionOrchestrator(provider=provider, policy=ExecutionPolicy.for_chat())


def test_plan_initial_step_on_fresh_execution():
    execution = Execution.new(origin="chat")
    orchestrator = _orchestrator(_ScriptedProvider([_respond_json(execution.execution_id)]))

    step = plan_initial_step(orchestrator, execution, objective="pergunta", model="qualquer")

    assert step.action == Action.RESPOND
    assert execution.step_count == 1
    assert execution.status == ExecutionStatus.COMPLETED


def test_plan_initial_step_works_after_manual_start_with_no_steps():
    execution = Execution.new(origin="chat")
    execution.start()  # já RUNNING, mas ainda sem etapas
    orchestrator = _orchestrator(_ScriptedProvider([_respond_json(execution.execution_id)]))

    step = plan_initial_step(orchestrator, execution, objective="pergunta", model="qualquer")

    assert step is not None
    assert execution.step_count == 1


def test_plan_initial_step_raises_when_execution_already_has_steps():
    execution = Execution.new(origin="chat")
    orchestrator = _orchestrator(
        _ScriptedProvider([_respond_json(execution.execution_id), _respond_json(execution.execution_id)])
    )
    plan_initial_step(orchestrator, execution, objective="pergunta", model="qualquer")

    with pytest.raises(ExecutionAlreadyPlannedError):
        plan_initial_step(orchestrator, execution, objective="outra pergunta", model="qualquer")
