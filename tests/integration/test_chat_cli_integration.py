"""Teste de integração: cenário real fixo do CLI/chat de teste (TASK-084)
ponta a ponta — o payload que `scripts/chat.py` monta é enviado de
verdade para `POST /v1/executions` (`fastapi.testclient.TestClient`,
com `LocalLLMProvider` fake, mesmo padrão de
`tests/integration/test_api_executions_integration.py`) e a resposta
real é interpretada por `chat.format_response`. Usa a fixture
`postgres_dsn` (tests/integration/conftest.py) — pula automaticamente
se o banco não estiver disponível.
"""

import json
import re
import sys
import uuid
from pathlib import Path

import psycopg
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import chat  # noqa: E402

from app.api.app import app
from app.api.dependencies import get_active_model, get_local_llm_provider
from app.auth.api_keys import create_application
from app.llm.provider import CompletionRequest, CompletionResponse, LocalLLMProvider

_EXECUTION_ID_PATTERN = re.compile(r"Execução atual: ([0-9a-fA-F-]+)")


class _AutoRespondProvider(LocalLLMProvider):
    def complete(self, request: CompletionRequest) -> CompletionResponse:
        match = _EXECUTION_ID_PATTERN.search(request.prompt)
        assert match is not None, "prompt sem execution_id reconhecível"
        text = json.dumps(
            {
                "execution_id": match.group(1),
                "action": "RESPOND",
                "confidence": "HIGH",
                "reason": "resposta do chat de teste",
            },
            ensure_ascii=False,
        )
        return CompletionResponse(text=text, model=request.model)

    def is_available(self) -> bool:
        return True


@pytest.fixture
def registered_application(postgres_dsn):
    name = f"teste_task084_{uuid.uuid4().hex[:12]}"
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


def test_chat_cli_payload_produces_real_successful_execution(
    postgres_dsn, registered_application, client
):
    _, api_key = registered_application
    payload = chat.build_execution_payload("qual é a capital da frança?", 30.0)

    response = client.post(
        "/v1/executions", json=payload, headers={"Authorization": f"Bearer {api_key}"}
    )

    result = chat.format_response(response.status_code, response.json())

    assert result.ok is True
    assert result.message == "resposta do chat de teste"


def test_chat_cli_payload_reports_real_auth_error(postgres_dsn, client):
    payload = chat.build_execution_payload("oi", 30.0)

    response = client.post(
        "/v1/executions", json=payload, headers={"Authorization": "Bearer cldk_naoexiste"}
    )

    result = chat.format_response(response.status_code, response.json())

    assert result.ok is False
    assert "2002" in result.message
    assert "401" in result.message
