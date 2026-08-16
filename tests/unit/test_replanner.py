"""Testes unitários do replanejamento completo (TASK-027), com provider fake."""

import json

import pytest

from app.errors.response import ClaudiaoError
from app.llm.provider import CompletionRequest, CompletionResponse, LocalLLMProvider
from app.orchestrator.execution import Execution, ExecutionStatus
from app.orchestrator.orchestrator import ExecutionOrchestrator
from app.orchestrator.replanner import CannotReplanFinishedExecutionError, replan
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
            "reason": "novo plano, resposta pronta",
        }
    )


def _use_tool_json(execution_id: str, tool: str = "WEB_SEARCH") -> str:
    return json.dumps(
        {
            "execution_id": execution_id,
            "action": "USE_TOOL",
            "tool": tool,
            "confidence": "LOW",
            "reason": "preciso pesquisar de novo",
            "parameters": {},
        }
    )


def _orchestrator(provider: LocalLLMProvider, web_search_allowed: bool = True) -> ExecutionOrchestrator:
    return ExecutionOrchestrator(
        provider=provider, policy=ExecutionPolicy.for_chat(web_search_allowed=web_search_allowed)
    )


def test_replan_discards_old_execution_and_creates_new_one():
    old_execution = Execution.new(origin="chat")
    old_execution.start()
    # Provider serve a nova execução — seu execution_id só existe depois de
    # Execution.new() rodar dentro de replan(), então respondemos de forma
    # dinâmica via lambda-like scripted provider abaixo.

    class _DynamicProvider(LocalLLMProvider):
        def complete(self, request: CompletionRequest) -> CompletionResponse:
            # extrai o novo execution_id embutido no próprio prompt composto
            import re

            match = re.search(r"Execução atual: ([0-9a-f-]{36})", request.prompt)
            new_id = match.group(1)
            return CompletionResponse(text=_respond_json(new_id), model=request.model)

        def is_available(self) -> bool:
            return True

    orchestrator = _orchestrator(_DynamicProvider())

    new_execution, step = replan(orchestrator, old_execution, objective="pergunta nova", model="qualquer")

    assert old_execution.status == ExecutionStatus.FAILED
    assert new_execution.execution_id != old_execution.execution_id
    assert new_execution.origin == old_execution.origin
    assert new_execution.step_count == 1
    assert step.reason == "novo plano, resposta pronta"


def test_replan_preserves_old_execution_step_history():
    old_execution = Execution.new(origin="application")
    provider_for_old = _ScriptedProvider([_use_tool_json(old_execution.execution_id)])
    _orchestrator(provider_for_old).run_step(old_execution, objective="pergunta", model="qualquer")
    assert old_execution.step_count == 1  # tinha progresso antes do replan

    class _DynamicProvider(LocalLLMProvider):
        def complete(self, request: CompletionRequest) -> CompletionResponse:
            import re

            match = re.search(r"Execução atual: ([0-9a-f-]{36})", request.prompt)
            return CompletionResponse(text=_respond_json(match.group(1)), model=request.model)

        def is_available(self) -> bool:
            return True

    orchestrator = _orchestrator(_DynamicProvider())
    new_execution, _step = replan(orchestrator, old_execution, objective="pergunta", model="qualquer")

    assert old_execution.step_count == 1  # histórico antigo não é apagado
    assert old_execution.status == ExecutionStatus.FAILED
    assert new_execution.step_count == 1  # execução nova começa do zero


def test_replan_raises_for_already_completed_execution():
    execution = Execution.new(origin="chat")
    provider = _ScriptedProvider([_respond_json(execution.execution_id)])
    _orchestrator(provider).run_step(execution, objective="pergunta", model="qualquer")
    assert execution.status == ExecutionStatus.COMPLETED

    with pytest.raises(CannotReplanFinishedExecutionError):
        replan(_orchestrator(_ScriptedProvider([])), execution, objective="outra", model="qualquer")

    assert execution.status == ExecutionStatus.COMPLETED  # não foi alterado


def test_replan_raises_for_already_failed_execution():
    execution = Execution.new(origin="chat")
    execution.start()
    execution.fail("erro qualquer")

    with pytest.raises(CannotReplanFinishedExecutionError):
        replan(_orchestrator(_ScriptedProvider([])), execution, objective="outra", model="qualquer")


def test_replan_new_plan_goes_through_plan_validation():
    """"Mesmas regras do plano inicial" (TASK-025) — WEB_SEARCH sem
    autorização no novo plano deve falhar a nova execução, não passar
    despercebido só porque veio de um replanejamento."""
    old_execution = Execution.new(origin="chat")
    old_execution.start()

    class _DynamicProvider(LocalLLMProvider):
        def complete(self, request: CompletionRequest) -> CompletionResponse:
            import re

            match = re.search(r"Execução atual: ([0-9a-f-]{36})", request.prompt)
            return CompletionResponse(
                text=_use_tool_json(match.group(1)), model=request.model
            )

        def is_available(self) -> bool:
            return True

    orchestrator = _orchestrator(_DynamicProvider(), web_search_allowed=False)

    with pytest.raises(ClaudiaoError):
        replan(orchestrator, old_execution, objective="pergunta", model="qualquer")
