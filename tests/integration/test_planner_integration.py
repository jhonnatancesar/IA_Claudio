"""Teste de integração: plan_initial_step + OllamaProvider real (TASK-024).
Usa a fixture `ollama_provider` (tests/integration/conftest.py) — pula
automaticamente se o Ollama não estiver acessível.

Sem modelo baixado nesta máquina (docs/OPEN_QUESTIONS.md, item 3), então
valida o caminho de falha correto, igual ao teste de integração da TASK-023.
"""

import pytest

from app.llm.provider import LocalLLMProviderError
from app.orchestrator.execution import Execution, ExecutionStatus
from app.orchestrator.orchestrator import ExecutionOrchestrator
from app.orchestrator.planner import plan_initial_step
from app.policies.execution_policy import ExecutionPolicy


def test_plan_initial_step_against_real_ollama_with_missing_model(ollama_provider):
    orchestrator = ExecutionOrchestrator(
        provider=ollama_provider, policy=ExecutionPolicy.for_chat()
    )
    execution = Execution.new(origin="chat")

    with pytest.raises(LocalLLMProviderError):
        plan_initial_step(
            orchestrator,
            execution,
            objective="pergunta qualquer",
            model="modelo-que-certamente-nao-existe-no-ollama-local",
        )

    assert execution.status == ExecutionStatus.FAILED
    assert execution.step_count == 0
