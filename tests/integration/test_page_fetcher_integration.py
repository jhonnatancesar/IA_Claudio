"""Teste de integração: open_page contra uma página real. Usa a instância
local do SearXNG (TASK-089, já rodando via Docker para outros testes) em
vez da internet pública, para não depender de um site de terceiro
instável/fora do nosso controle — pula automaticamente se ela não estiver
acessível, mesmo padrão de `postgres_dsn`/`ollama_provider`/
`searxng_provider` (tests/conftest.py)."""

import pytest

from app.web_search.page_fetcher import PageFetchError, open_page
from app.web_search.providers.searxng_provider import DEFAULT_BASE_URL, SearXNGSearchProvider


@pytest.fixture
def local_http_url():
    provider = SearXNGSearchProvider(base_url=DEFAULT_BASE_URL)
    if not provider.is_available():
        pytest.skip("Nenhum servidor HTTP local acessível — pulando teste de integração.")
    return DEFAULT_BASE_URL + "/"


def test_open_page_returns_real_html_content(local_http_url):
    page = open_page(local_http_url)

    assert page.status_code == 200
    assert "html" in page.content_type
    assert len(page.body) > 0


def test_open_page_raises_page_fetch_error_for_unreachable_host():
    with pytest.raises(PageFetchError):
        open_page("http://localhost:1/pagina-inexistente", timeout=2.0)
