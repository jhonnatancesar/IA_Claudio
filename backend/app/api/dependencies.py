"""Dependências de execução síncrona da API (TASK-069).

Constrói o `LocalLLMProvider` (`OllamaProvider`, TASK-015) e resolve o
modelo ativo usados pela rota de execuções, como dependências do FastAPI
— podem ser substituídas por fakes nos testes via
`app.dependency_overrides`, sem exigir um modelo Ollama de verdade
baixado (nenhum foi, `docs/OPEN_QUESTIONS.md`, item 3).

O modelo ativo vem de `CLAUDIAO_ACTIVE_MODEL` (`config/.env.example`, já
previsto desde a TASK-002); a escolha do modelo definitivo continua em
aberto — se a variável não estiver configurada, a rota falha com um erro
claro (`NO_ACTIVE_MODEL_CONFIGURED`) em vez de tentar completar com um
nome de modelo vazio.
"""

from __future__ import annotations

import os

from app.errors.catalog import ErrorDomain, register_error
from app.errors.response import ClaudiaoError
from app.llm.provider import LocalLLMProvider
from app.llm.providers.ollama_provider import OllamaProvider

NO_ACTIVE_MODEL_CONFIGURED = register_error(
    ErrorDomain.TOOLS_PROVIDERS, 3001, 503, "Nenhum modelo local ativo configurado"
)


def get_local_llm_provider() -> LocalLLMProvider:
    return OllamaProvider()


def get_active_model() -> str:
    """Lê `CLAUDIAO_ACTIVE_MODEL` do ambiente. Levanta `ClaudiaoError`
    (`NO_ACTIVE_MODEL_CONFIGURED`) se não estiver configurado."""
    model = os.environ.get("CLAUDIAO_ACTIVE_MODEL")
    if not model:
        raise ClaudiaoError(NO_ACTIVE_MODEL_CONFIGURED)
    return model
