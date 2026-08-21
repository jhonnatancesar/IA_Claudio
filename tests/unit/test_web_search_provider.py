"""Testes unitários da interface WebSearchProvider (TASK-088). Sem rede real
— TASK-089 é a primeira implementação concreta."""

import pytest

from app.web_search.provider import (
    SearchPurpose,
    SearchRequest,
    SearchResponse,
    SearchResult,
    WebSearchProvider,
    WebSearchProviderError,
)


class _FakeProvider(WebSearchProvider):
    """Implementação mínima só para testar o contrato da interface."""

    def __init__(self, *, available: bool = True) -> None:
        self._available = available

    def search(self, request: SearchRequest) -> SearchResponse:
        if not self._available:
            raise WebSearchProviderError("serviço indisponível")
        return SearchResponse(
            results=[
                SearchResult(
                    url="https://exemplo.com",
                    title=f"resultado para {request.query}",
                    snippet="trecho de exemplo",
                )
            ],
            raw={"ok": True},
        )

    def is_available(self) -> bool:
        return self._available


def test_web_search_provider_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        WebSearchProvider()  # classe abstrata


def test_subclass_missing_abstract_method_cannot_be_instantiated():
    class _IncompleteProvider(WebSearchProvider):
        def search(self, request):  # falta is_available
            raise NotImplementedError

    with pytest.raises(TypeError):
        _IncompleteProvider()


def test_search_request_is_frozen():
    request = SearchRequest(
        query="claudião", max_results=5, purpose=SearchPurpose.GENERAL_RESEARCH
    )

    with pytest.raises(AttributeError):
        request.query = "outra coisa"


def test_search_request_metadata_defaults_to_empty_dict():
    request = SearchRequest(
        query="claudião", max_results=5, purpose=SearchPurpose.GENERAL_RESEARCH
    )

    assert request.metadata == {}


def test_search_purpose_has_the_four_documented_values():
    assert {purpose.value for purpose in SearchPurpose} == {
        "GENERAL_RESEARCH",
        "ENTITY_VERIFICATION",
        "CURRENT_INFORMATION",
        "PRODUCT_IDENTITY",
    }


def test_fake_provider_search_returns_search_response():
    provider = _FakeProvider()
    request = SearchRequest(
        query="claudião", max_results=5, purpose=SearchPurpose.GENERAL_RESEARCH
    )

    response = provider.search(request)

    assert isinstance(response, SearchResponse)
    assert len(response.results) == 1
    assert response.results[0].url == "https://exemplo.com"
    assert response.results[0].title == "resultado para claudião"
    assert response.raw == {"ok": True}


def test_fake_provider_raises_web_search_provider_error_when_unavailable():
    provider = _FakeProvider(available=False)
    request = SearchRequest(
        query="claudião", max_results=5, purpose=SearchPurpose.GENERAL_RESEARCH
    )

    with pytest.raises(WebSearchProviderError):
        provider.search(request)


def test_fake_provider_is_available_reflects_state():
    assert _FakeProvider(available=True).is_available() is True
    assert _FakeProvider(available=False).is_available() is False
