"""Fixtures compartilhadas dos testes com serviços locais reais
(PostgreSQL, Ollama). Extraído do teste de integração da TASK-006 para
reaproveitar em outros módulos que também têm teste real (ex.: TASK-009,
autenticação; TASK-015, Ollama), sem duplicar a lógica de disponibilidade.

Movido de `tests/integration/conftest.py` para aqui na TASK-086 — os
cenários fixos de `tests/scenarios/` (`docs/TESTING.md`) também
precisam destas fixtures, e um `conftest.py` só se aplica aos testes
dentro do próprio diretório e subdiretórios (pytest); em
`tests/integration/` só alcançava `tests/integration/`, não
`tests/scenarios/`, que é um diretório irmão. Nenhuma mudança de
comportamento — só de local, mesmo espírito da TASK-009 movendo
`build_dsn_from_env` para `app.db.connection`.
"""

from pathlib import Path

import psycopg
import pytest

from app.db.connection import build_dsn_from_env
from app.llm.providers.ollama_provider import DEFAULT_HOST, OllamaProvider
from app.web_search.providers.searxng_provider import (
    DEFAULT_BASE_URL as SEARXNG_DEFAULT_BASE_URL,
    SearXNGSearchProvider,
)

_ENV_FILE = Path(__file__).resolve().parent.parent / "config" / ".env"
_REQUIRED_VARS = (
    "CLAUDIAO_POSTGRES_HOST",
    "CLAUDIAO_POSTGRES_PORT",
    "CLAUDIAO_POSTGRES_DB",
    "CLAUDIAO_POSTGRES_USER",
    "CLAUDIAO_POSTGRES_PASSWORD",
)


def _load_local_env_file(monkeypatch) -> None:
    """Carrega config/.env (não versionado — TASK-003) se as variáveis ainda não
    estiverem no ambiente. Parser simples, só para uso local de teste."""
    if not _ENV_FILE.exists():
        return
    for line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if key in _REQUIRED_VARS:
            monkeypatch.setenv(key, value.strip())


@pytest.fixture
def postgres_dsn(monkeypatch):
    """DSN de um PostgreSQL local acessível, ou pula o teste que a usar."""
    _load_local_env_file(monkeypatch)
    dsn = build_dsn_from_env()
    if dsn is None:
        pytest.skip(
            "Credenciais do PostgreSQL local não disponíveis "
            "(nem no ambiente, nem em config/.env) — pulando teste de integração."
        )
    try:
        with psycopg.connect(dsn, connect_timeout=3):
            pass
    except Exception as exc:
        pytest.skip(f"PostgreSQL local indisponível para o teste de integração: {exc}")
    return dsn


@pytest.fixture
def ollama_provider():
    """`OllamaProvider` contra um Ollama local acessível, ou pula o teste."""
    provider = OllamaProvider(host=DEFAULT_HOST)
    if not provider.is_available():
        pytest.skip("Ollama local indisponível — pulando teste de integração.")
    return provider


@pytest.fixture
def searxng_provider():
    """`SearXNGSearchProvider` contra uma instância local acessível (TASK-089,
    `docker run ... searxng/searxng`), ou pula o teste."""
    provider = SearXNGSearchProvider(base_url=SEARXNG_DEFAULT_BASE_URL)
    if not provider.is_available():
        pytest.skip("SearXNG local indisponível — pulando teste de integração.")
    return provider
