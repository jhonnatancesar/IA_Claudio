"""Testes unitários da interface LocalLLMProvider (TASK-014). Sem runtime real
— TASK-015 (OllamaProvider) é a primeira implementação concreta."""

import pytest

from app.llm.provider import (
    CompletionRequest,
    CompletionResponse,
    LocalLLMProvider,
    LocalLLMProviderError,
)


class _FakeProvider(LocalLLMProvider):
    """Implementação mínima só para testar o contrato da interface."""

    def __init__(self, *, available: bool = True) -> None:
        self._available = available

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        if not self._available:
            raise LocalLLMProviderError("runtime indisponível")
        return CompletionResponse(
            text=f"eco: {request.prompt}", model=request.model, raw={"ok": True}
        )

    def is_available(self) -> bool:
        return self._available


def test_local_llm_provider_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        LocalLLMProvider()  # classe abstrata


def test_subclass_missing_abstract_method_cannot_be_instantiated():
    class _IncompleteProvider(LocalLLMProvider):
        def complete(self, request):  # falta is_available
            raise NotImplementedError

    with pytest.raises(TypeError):
        _IncompleteProvider()


def test_completion_request_has_sane_defaults():
    request = CompletionRequest(prompt="olá", model="algum-modelo")

    assert request.temperature == 0.0
    assert request.max_tokens is None
    assert request.metadata == {}


def test_completion_request_is_frozen():
    request = CompletionRequest(prompt="olá", model="algum-modelo")

    with pytest.raises(AttributeError):
        request.prompt = "outra coisa"


def test_fake_provider_complete_returns_completion_response():
    provider = _FakeProvider()
    request = CompletionRequest(prompt="teste", model="algum-modelo")

    response = provider.complete(request)

    assert isinstance(response, CompletionResponse)
    assert response.text == "eco: teste"
    assert response.model == "algum-modelo"
    assert response.raw == {"ok": True}


def test_fake_provider_raises_local_llm_provider_error_when_unavailable():
    provider = _FakeProvider(available=False)
    request = CompletionRequest(prompt="teste", model="algum-modelo")

    with pytest.raises(LocalLLMProviderError):
        provider.complete(request)


def test_fake_provider_is_available_reflects_state():
    assert _FakeProvider(available=True).is_available() is True
    assert _FakeProvider(available=False).is_available() is False
