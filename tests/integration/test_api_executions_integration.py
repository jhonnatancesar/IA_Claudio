"""Teste de integração: API local do Claudião (TASK-067, TASK-068,
TASK-069, TASK-070) executando de verdade contra o PostgreSQL local —
autenticação real de aplicação, validação de payload e execução síncrona
via HTTP. Usa a fixture `postgres_dsn` (tests/integration/conftest.py) —
pula automaticamente se o banco não estiver disponível.

O `LocalLLMProvider`/modelo ativo são substituídos por fakes via
`app.dependency_overrides` (TASK-069) — nenhum modelo Ollama real foi
baixado nesta máquina (`docs/OPEN_QUESTIONS.md`, item 3), então testar a
execução síncrona de ponta a ponta exige um provider fake, mesmo padrão
já usado em `tests/unit/test_execution_orchestrator.py`.
"""

import json
import re
import time
import uuid

import psycopg
import pytest
from fastapi.testclient import TestClient

from app.api.app import app
from app.api.dependencies import get_active_model, get_local_llm_provider
from app.auth.api_keys import create_application
from app.llm.provider import (
    CompletionRequest,
    CompletionResponse,
    LocalLLMProvider,
    LocalLLMProviderError,
)

_VALID_PAYLOAD = {
    "objective": "buscar o clima de hoje",
    "usage_type": "chat",
    "web_search_allowed": True,
    "timeout_seconds": 30,
}

_EXECUTION_ID_PATTERN = re.compile(r"Execução atual: ([0-9a-fA-F-]+)")


class _AutoRespondProvider(LocalLLMProvider):
    """Provider fake que sempre responde `RESPOND` de primeira, extraindo
    o `execution_id` do próprio prompt composto (TASK-019) — o endpoint
    gera o `execution_id` internamente, então o teste não pode sabê-lo de
    antemão."""

    def __init__(self, reason: str = "resposta pronta") -> None:
        self._reason = reason

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        match = _EXECUTION_ID_PATTERN.search(request.prompt)
        assert match is not None, "prompt sem execution_id reconhecível"
        text = json.dumps(
            {
                "execution_id": match.group(1),
                "action": "RESPOND",
                "confidence": "HIGH",
                "reason": self._reason,
            },
            ensure_ascii=False,
        )
        return CompletionResponse(text=text, model=request.model)

    def is_available(self) -> bool:
        return True


class _FailingProvider(LocalLLMProvider):
    """Provider fake que sempre levanta `LocalLLMProviderError`."""

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        raise LocalLLMProviderError("timeout simulado ao chamar o modelo")

    def is_available(self) -> bool:
        return False


class _SlowProvider(LocalLLMProvider):
    """Provider fake que demora mais que o `timeout_seconds` do payload
    antes de responder (TASK-070) — simula um modelo local travado."""

    def __init__(self, delay_seconds: float, reason: str = "resposta atrasada") -> None:
        self._delay_seconds = delay_seconds
        self._reason = reason

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        time.sleep(self._delay_seconds)
        match = _EXECUTION_ID_PATTERN.search(request.prompt)
        assert match is not None, "prompt sem execution_id reconhecível"
        text = json.dumps(
            {
                "execution_id": match.group(1),
                "action": "RESPOND",
                "confidence": "HIGH",
                "reason": self._reason,
            },
            ensure_ascii=False,
        )
        return CompletionResponse(text=text, model=request.model)

    def is_available(self) -> bool:
        return True


@pytest.fixture
def registered_application(postgres_dsn):
    name = f"teste_task067_{uuid.uuid4().hex[:12]}"
    application, api_key = create_application(name)
    yield application, api_key
    with psycopg.connect(postgres_dsn) as conn:
        conn.execute("DELETE FROM applications WHERE id = %s", (application.id,))


@pytest.fixture
def client():
    app.dependency_overrides[get_active_model] = lambda: "modelo-de-teste"
    app.dependency_overrides[get_local_llm_provider] = lambda: _AutoRespondProvider()
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_create_execution_with_valid_payload(postgres_dsn, registered_application, client):
    _, api_key = registered_application

    response = client.post(
        "/v1/executions",
        json=_VALID_PAYLOAD,
        headers={"Authorization": f"Bearer {api_key}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "execution_id" in body
    assert body["status"] == "COMPLETED"
    assert body["result"] == "resposta pronta"


def test_create_execution_generates_unique_execution_ids(
    postgres_dsn, registered_application, client
):
    _, api_key = registered_application
    headers = {"Authorization": f"Bearer {api_key}"}

    first = client.post("/v1/executions", json=_VALID_PAYLOAD, headers=headers)
    second = client.post("/v1/executions", json=_VALID_PAYLOAD, headers=headers)

    assert first.json()["execution_id"] != second.json()["execution_id"]


def test_create_execution_without_api_key_is_rejected(postgres_dsn, client):
    response = client.post("/v1/executions", json=_VALID_PAYLOAD)

    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == 2002


def test_create_execution_with_invalid_api_key_is_rejected(postgres_dsn, client):
    response = client.post(
        "/v1/executions", json=_VALID_PAYLOAD, headers={"Authorization": "Bearer cldk_naoexiste"}
    )

    assert response.status_code == 401
    assert response.json()["success"] is False


def test_create_execution_missing_required_field_is_rejected(
    postgres_dsn, registered_application, client
):
    _, api_key = registered_application
    payload = {k: v for k, v in _VALID_PAYLOAD.items() if k != "objective"}

    response = client.post(
        "/v1/executions", json=payload, headers={"Authorization": f"Bearer {api_key}"}
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == 1001
    assert body["error"]["details"]["errors"][0]["field"] == "body.objective"


def test_create_execution_invalid_field_value_is_rejected(
    postgres_dsn, registered_application, client
):
    _, api_key = registered_application
    payload = {**_VALID_PAYLOAD, "timeout_seconds": -5}

    response = client.post(
        "/v1/executions", json=payload, headers={"Authorization": f"Bearer {api_key}"}
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == 1002


def test_create_execution_empty_body_is_rejected(postgres_dsn, registered_application, client):
    _, api_key = registered_application

    response = client.post(
        "/v1/executions", json={}, headers={"Authorization": f"Bearer {api_key}"}
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == 1001


def test_create_execution_reports_model_completion_failure(
    postgres_dsn, registered_application, client
):
    _, api_key = registered_application
    app.dependency_overrides[get_local_llm_provider] = lambda: _FailingProvider()

    response = client.post(
        "/v1/executions", json=_VALID_PAYLOAD, headers={"Authorization": f"Bearer {api_key}"}
    )

    assert response.status_code == 502
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == 3002


def test_create_execution_times_out_when_model_is_slower_than_timeout_seconds(
    postgres_dsn, registered_application, client
):
    _, api_key = registered_application
    app.dependency_overrides[get_local_llm_provider] = lambda: _SlowProvider(delay_seconds=0.5)
    payload = {**_VALID_PAYLOAD, "timeout_seconds": 0.05}

    started_at = time.monotonic()
    response = client.post(
        "/v1/executions", json=payload, headers={"Authorization": f"Bearer {api_key}"}
    )
    elapsed = time.monotonic() - started_at

    assert response.status_code == 504
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == 4009
    details = body["error"]["details"]
    assert details["timeout_seconds"] == 0.05
    # provider trava na primeira chamada ao modelo: nenhuma etapa chegou a
    # ser registrada ainda, então é a 1ª etapa que travou, sem ferramenta
    # ativa (TASK-071).
    assert details["current_step"] == 1
    assert details["active_tool"] is None
    # a resposta HTTP não espera o provider travado terminar (0.5s) — só o
    # timeout configurado (0.05s), com folga generosa para o overhead do
    # próprio teste.
    assert elapsed < 0.5


def test_create_execution_completes_normally_when_faster_than_timeout_seconds(
    postgres_dsn, registered_application, client
):
    _, api_key = registered_application
    app.dependency_overrides[get_local_llm_provider] = lambda: _SlowProvider(delay_seconds=0.01)
    payload = {**_VALID_PAYLOAD, "timeout_seconds": 5}

    response = client.post(
        "/v1/executions", json=payload, headers={"Authorization": f"Bearer {api_key}"}
    )

    assert response.status_code == 200
    assert response.json()["result"] == "resposta atrasada"


def test_create_execution_without_active_model_configured(
    postgres_dsn, registered_application, client, monkeypatch
):
    _, api_key = registered_application
    monkeypatch.delenv("CLAUDIAO_ACTIVE_MODEL", raising=False)
    # `client` já sobrescreveu `get_active_model` com um fake — remove essa
    # sobrescrita para exercitar a função real (leitura do ambiente).
    del app.dependency_overrides[get_active_model]

    response = client.post(
        "/v1/executions", json=_VALID_PAYLOAD, headers={"Authorization": f"Bearer {api_key}"}
    )

    assert response.status_code == 503
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == 3001
