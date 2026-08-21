"""Teste de integração: OllamaProvider contra o Ollama local de verdade
(TASK-015). Usa a fixture `ollama_provider` (tests/conftest.py) —
pula automaticamente se o Ollama não estiver acessível.

Nenhum modelo foi baixado nesta máquina (docs/OPEN_QUESTIONS.md, item 3), então
não testamos uma geração bem-sucedida aqui (isso exigiria um modelo real) — só
o que dá para verificar sem depender de um modelo específico: disponibilidade
do servidor e o mapeamento de erro para modelo inexistente.
"""

import pytest

from app.llm.provider import CompletionRequest, LocalLLMProviderError


def test_is_available_true_against_real_ollama(ollama_provider):
    assert ollama_provider.is_available() is True


def test_complete_with_unknown_model_raises_local_llm_provider_error(ollama_provider):
    request = CompletionRequest(
        prompt="olá", model="modelo-que-certamente-nao-existe-no-ollama-local"
    )

    with pytest.raises(LocalLLMProviderError):
        ollama_provider.complete(request)
