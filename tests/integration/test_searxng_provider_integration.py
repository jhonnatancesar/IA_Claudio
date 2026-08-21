"""Teste de integração: SearXNGSearchProvider contra uma instância SearXNG
local de verdade (TASK-089, `docker run ... searxng/searxng`). Usa a
fixture `searxng_provider` (tests/conftest.py) — pula automaticamente se o
SearXNG não estiver acessível.
"""

from app.web_search.provider import SearchPurpose, SearchRequest


def test_is_available_true_against_real_searxng(searxng_provider):
    assert searxng_provider.is_available() is True


def test_search_returns_real_results_for_a_general_query(searxng_provider):
    request = SearchRequest(
        query="python programming language",
        max_results=5,
        purpose=SearchPurpose.GENERAL_RESEARCH,
    )

    response = searxng_provider.search(request)

    assert len(response.results) > 0
    assert len(response.results) <= 5
    assert all(result.url for result in response.results)
    assert all(result.title for result in response.results)


def test_search_respects_max_results(searxng_provider):
    request = SearchRequest(
        query="python", max_results=2, purpose=SearchPurpose.GENERAL_RESEARCH
    )

    response = searxng_provider.search(request)

    assert len(response.results) <= 2
