"""Teste de integração: ExecutionOrchestrator + OllamaProvider real
(TASK-023). Usa a fixture `ollama_provider` (tests/integration/conftest.py) —
pula automaticamente se o Ollama não estiver acessível.

Sem modelo baixado nesta máquina (docs/OPEN_QUESTIONS.md, item 3), então este
teste valida o caminho de falha correto: o provider real recusa um modelo
inexistente, e a Execution deve terminar FAILED — não travar nem vazar outra
exceção.
"""

import pytest

from app.llm.provider import LocalLLMProviderError
from app.orchestrator.execution import Execution, ExecutionStatus
from app.orchestrator.orchestrator import ExecutionOrchestrator
from app.policies.execution_policy import ExecutionPolicy


def test_run_step_against_real_ollama_with_missing_model_fails_execution(
    ollama_provider,
):
    orchestrator = ExecutionOrchestrator(
        provider=ollama_provider, policy=ExecutionPolicy.for_chat()
    )
    execution = Execution.new(origin="chat")

    with pytest.raises(LocalLLMProviderError):
        orchestrator.run_step(
            execution,
            objective="pergunta qualquer",
            model="modelo-que-certamente-nao-existe-no-ollama-local",
        )

    assert execution.status == ExecutionStatus.FAILED
