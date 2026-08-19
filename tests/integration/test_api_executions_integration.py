"""Teste de integração: API local do Claudião (TASK-067, TASK-068)
executando de verdade contra o PostgreSQL local — autenticação real de
aplicação, validação de payload e criação de execução via HTTP. Usa a
fixture `postgres_dsn` (tests/integration/conftest.py) — pula
automaticamente se o banco não estiver disponível.
"""

import uuid

import psycopg
import pytest
from fastapi.testclient import TestClient

from app.api.app import app
from app.auth.api_keys import create_application

_VALID_PAYLOAD = {
    "objective": "buscar o clima de hoje",
    "usage_type": "chat",
    "web_search_allowed": True,
    "timeout_seconds": 30,
}


@pytest.fixture
def registered_application(postgres_dsn):
    name = f"teste_task067_{uuid.uuid4().hex[:12]}"
    application, api_key = create_application(name)
    yield application, api_key
    with psycopg.connect(postgres_dsn) as conn:
        conn.execute("DELETE FROM applications WHERE id = %s", (application.id,))


@pytest.fixture
def client():
    return TestClient(app)


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
    assert body["status"] == "PENDING"


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
