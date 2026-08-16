"""Testes unitários da aplicação de max_steps (TASK-028), com providers e
tool_executor fakes."""

import json

import pytest

from app.errors.response import ClaudiaoError
from app.llm.provider import CompletionRequest, CompletionResponse, LocalLLMProvider
from app.orchestrator.execution import Execution, ExecutionStatus
from app.orchestrator.orchestrator import MAX_STEPS_EXCEEDED, ExecutionOrchestrator
from app.policies.execution_policy import ExecutionPolicy


class _ScriptedProvider(LocalLLMProvider):
    def __init__(self, responses: list[str]) -> None:
        self._responses = list(responses)

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        return CompletionResponse(text=self._responses.pop(0), model=request.model)

    def is_available(self) -> bool:
        return True


class _InfiniteToolProvider(LocalLLMProvider):
    """Sempre pede a mesma ferramenta, mas com parâmetros diferentes a cada
    vez (progresso real, não repetição) — nunca decide RESPOND. Simula um
    modelo que não converge, cenário que max_steps precisa conter. Varia os
    parâmetros de propósito para não disparar a detecção de loop (TASK-029),
    testada à parte, e isolar o comportamento de max_steps aqui."""

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
                    "reason": "preciso pesquisar de novo",
                    "parameters": {"query": f"tentativa {self._count}"},
                }
            ),
            model=request.model,
        )

    def is_available(self) -> bool:
        return True


def _respond_json(execution_id: str) -> str:
    return json.dumps(
        {
            "execution_id": execution_id,
            "action": "RESPOND",
            "confidence": "HIGH",
            "reason": "resposta pronta",
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
            "parameters": {},
        }
    )


def test_run_step_raises_when_step_count_already_at_max_steps():
    # USE_TOOL no primeiro passo: a execução continua RUNNING (não termina
    # sozinha), então o segundo run_step realmente testa o limite de
    # max_steps — com RESPOND, a execução já teria concluído antes disso.
    execution = Execution.new(origin="chat")
    provider = _ScriptedProvider([_use_tool_json(execution.execution_id)])
    orchestrator = ExecutionOrchestrator(
        provider=provider,
        policy=ExecutionPolicy.for_chat(web_search_allowed=True, max_steps=1),
    )
    orchestrator.run_step(execution, objective="pergunta", model="qualquer")
    assert execution.step_count == 1
    assert execution.status == ExecutionStatus.RUNNING

    with pytest.raises(ClaudiaoError) as exc_info:
        orchestrator.run_step(execution, objective="pergunta", model="qualquer")

    assert exc_info.value.definition is MAX_STEPS_EXCEEDED
    assert execution.status == ExecutionStatus.FAILED
    assert execution.step_count == 1  # nenhuma etapa nova foi adicionada


def test_run_step_does_not_call_provider_when_limit_already_reached():
    """A checagem de max_steps acontece antes de chamar o modelo — não gasta
    uma chamada real ao provider."""
    execution = Execution.new(origin="chat")

    class _CountingProvider(LocalLLMProvider):
        def __init__(self) -> None:
            self.calls = 0

        def complete(self, request: CompletionRequest) -> CompletionResponse:
            self.calls += 1
            return CompletionResponse(text=_use_tool_json(execution.execution_id), model=request.model)

        def is_available(self) -> bool:
            return True

    provider = _CountingProvider()
    orchestrator = ExecutionOrchestrator(
        provider=provider,
        policy=ExecutionPolicy.for_chat(web_search_allowed=True, max_steps=1),
    )
    orchestrator.run_step(execution, objective="pergunta", model="qualquer")
    assert provider.calls == 1

    with pytest.raises(ClaudiaoError):
        orchestrator.run_step(execution, objective="pergunta", model="qualquer")

    assert provider.calls == 1  # não chamou o provider de novo


def test_run_until_response_stops_at_max_steps_when_never_responds():
    execution = Execution.new(origin="chat")
    orchestrator = ExecutionOrchestrator(
        provider=_InfiniteToolProvider(execution.execution_id),
        policy=ExecutionPolicy.for_chat(web_search_allowed=True, max_steps=3),
        tool_executor=lambda step: "resultado",
    )

    with pytest.raises(ClaudiaoError) as exc_info:
        orchestrator.run_until_response(execution, objective="pergunta", model="qualquer")

    assert exc_info.value.definition is MAX_STEPS_EXCEEDED
    assert execution.status == ExecutionStatus.FAILED
    assert execution.step_count == 3  # exatamente max_steps, nunca mais


def test_run_until_response_completes_normally_below_max_steps():
    execution = Execution.new(origin="chat")
    provider = _ScriptedProvider([_respond_json(execution.execution_id)])
    orchestrator = ExecutionOrchestrator(
        provider=provider, policy=ExecutionPolicy.for_chat(max_steps=10)
    )

    step = orchestrator.run_until_response(execution, objective="pergunta", model="qualquer")

    assert step.reason == "resposta pronta"
    assert execution.status == ExecutionStatus.COMPLETED


def test_default_max_steps_is_ten_and_allows_ten_steps():
    execution = Execution.new(origin="chat")
    orchestrator = ExecutionOrchestrator(
        provider=_InfiniteToolProvider(execution.execution_id),
        policy=ExecutionPolicy.for_chat(web_search_allowed=True),  # default max_steps=10
        tool_executor=lambda step: "resultado",
    )

    with pytest.raises(ClaudiaoError):
        orchestrator.run_until_response(execution, objective="pergunta", model="qualquer")

    assert execution.step_count == 10
