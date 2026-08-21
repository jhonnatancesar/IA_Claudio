"""Testes unitários do SearXNGSearchProvider (TASK-089), com `_fetch`
mockado — sem depender de uma instância SearXNG real. Validação contra o
SearXNG de verdade está em
tests/integration/test_searxng_provider_integration.py."""

import json
from unittest.mock import MagicMock

import pytest

from app.web_search.provider import SearchPurpose, SearchRequest, WebSearchProviderError
from app.web_search.providers.searxng_provider import SearXNGSearchProvider


def _provider_with_mock_fetch() -> tuple[SearXNGSearchProvider, MagicMock]:
    provider = SearXNGSearchProvider(base_url="http://host-nao-usado:8888")
    mock_fetch = MagicMock()
    provider._fetch = mock_fetch
    return provider, mock_fetch


def _request(query: str = "claudião", max_results: int = 10) -> SearchRequest:
    return SearchRequest(query=query, max_results=max_results, purpose=SearchPurpose.GENERAL_RESEARCH)


def test_search_maps_results_from_json_response():
    provider, mock_fetch = _provider_with_mock_fetch()
    mock_fetch.return_value = json.dumps(
        {
            "results": [
                {"url": "https://exemplo.com/a", "title": "Título A", "content": "trecho A"},
                {"url": "https://exemplo.com/b", "title": "Título B", "content": "trecho B"},
            ]
        }
    ).encode("utf-8")

    response = provider.search(_request())

    assert len(response.results) == 2
    assert response.results[0].url == "https://exemplo.com/a"
    assert response.results[0].title == "Título A"
    assert response.results[0].snippet == "trecho A"


def test_search_passes_query_and_json_format_in_url():
    provider, mock_fetch = _provider_with_mock_fetch()
    mock_fetch.return_value = json.dumps({"results": []}).encode("utf-8")

    provider.search(_request(query="python programming"))

    called_url = mock_fetch.call_args[0][0]
    assert "q=python+programming" in called_url
    assert "format=json" in called_url


def test_search_truncates_results_to_max_results():
    provider, mock_fetch = _provider_with_mock_fetch()
    mock_fetch.return_value = json.dumps(
        {"results": [{"url": f"https://exemplo.com/{i}", "title": str(i), "content": ""} for i in range(5)]}
    ).encode("utf-8")

    response = provider.search(_request(max_results=2))

    assert len(response.results) == 2


def test_search_defaults_missing_content_to_empty_snippet():
    provider, mock_fetch = _provider_with_mock_fetch()
    mock_fetch.return_value = json.dumps(
        {"results": [{"url": "https://exemplo.com", "title": "sem content"}]}
    ).encode("utf-8")

    response = provider.search(_request())

    assert response.results[0].snippet == ""


def test_search_wraps_network_error_as_web_search_provider_error():
    provider, mock_fetch = _provider_with_mock_fetch()
    mock_fetch.side_effect = OSError("conexão recusada")

    with pytest.raises(WebSearchProviderError):
        provider.search(_request())


def test_search_wraps_invalid_json_as_web_search_provider_error():
    provider, mock_fetch = _provider_with_mock_fetch()
    mock_fetch.return_value = b"isto nao e json"

    with pytest.raises(WebSearchProviderError):
        provider.search(_request())


def test_is_available_true_when_fetch_succeeds():
    provider, mock_fetch = _provider_with_mock_fetch()
    mock_fetch.return_value = b"OK"

    assert provider.is_available() is True


def test_is_available_false_when_fetch_raises():
    provider, mock_fetch = _provider_with_mock_fetch()
    mock_fetch.side_effect = OSError("conexão recusada")

    assert provider.is_available() is False


def test_searxng_provider_is_a_web_search_provider():
    from app.web_search.provider import WebSearchProvider

    assert isinstance(SearXNGSearchProvider(), WebSearchProvider)
