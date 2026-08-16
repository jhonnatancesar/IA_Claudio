"""Testes unitários do OllamaProvider (TASK-015), com o client do SDK
mockado — sem depender do runtime Ollama real. Validação contra o Ollama de
verdade está em tests/integration/test_ollama_provider_integration.py."""

from unittest.mock import MagicMock

import ollama
import pytest

from app.llm.provider import CompletionRequest, LocalLLMProviderError
from app.llm.providers.ollama_provider import OllamaProvider


def _provider_with_mock_client() -> tuple[OllamaProvider, MagicMock]:
    provider = OllamaProvider(host="http://host-nao-usado:11434")
    mock_client = MagicMock()
    provider._client = mock_client
    return provider, mock_client


def test_complete_maps_successful_response():
    provider, mock_client = _provider_with_mock_client()
    mock_client.generate.return_value = {
        "model": "algum-modelo",
        "response": "resposta do modelo",
        "done": True,
    }
    request = CompletionRequest(prompt="olá", model="algum-modelo")

    response = provider.complete(request)

    assert response.text == "resposta do modelo"
    assert response.model == "algum-modelo"
    assert response.raw["done"] is True


def test_complete_passes_temperature_and_max_tokens_as_options():
    provider, mock_client = _provider_with_mock_client()
    mock_client.generate.return_value = {"response": "ok"}
    request = CompletionRequest(
        prompt="olá", model="algum-modelo", temperature=0.7, max_tokens=128
    )

    provider.complete(request)

    _, kwargs = mock_client.generate.call_args
    assert kwargs["options"]["temperature"] == 0.7
    assert kwargs["options"]["num_predict"] == 128


def test_complete_omits_num_predict_when_max_tokens_not_set():
    provider, mock_client = _provider_with_mock_client()
    mock_client.generate.return_value = {"response": "ok"}
    request = CompletionRequest(prompt="olá", model="algum-modelo")

    provider.complete(request)

    _, kwargs = mock_client.generate.call_args
    assert "num_predict" not in kwargs["options"]


def test_complete_wraps_response_error_as_local_llm_provider_error():
    provider, mock_client = _provider_with_mock_client()
    mock_client.generate.side_effect = ollama.ResponseError("modelo não encontrado")
    request = CompletionRequest(prompt="olá", model="modelo-inexistente")

    with pytest.raises(LocalLLMProviderError):
        provider.complete(request)


def test_complete_wraps_connection_error_as_local_llm_provider_error():
    provider, mock_client = _provider_with_mock_client()
    mock_client.generate.side_effect = ConnectionError("servidor fora do ar")
    request = CompletionRequest(prompt="olá", model="algum-modelo")

    with pytest.raises(LocalLLMProviderError):
        provider.complete(request)


def test_is_available_true_when_list_succeeds():
    provider, mock_client = _provider_with_mock_client()
    mock_client.list.return_value = {"models": []}

    assert provider.is_available() is True


def test_is_available_false_when_list_raises():
    provider, mock_client = _provider_with_mock_client()
    mock_client.list.side_effect = ConnectionError("servidor fora do ar")

    assert provider.is_available() is False


def test_ollama_provider_is_a_local_llm_provider():
    from app.llm.provider import LocalLLMProvider

    assert isinstance(OllamaProvider(), LocalLLMProvider)
