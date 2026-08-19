"""Teste de integração: API local do Claudião (TASK-067) executando de
verdade contra o PostgreSQL local — autenticação real de aplicação e
criação de execução via HTTP. Usa a fixture `postgres_dsn`
(tests/integration/conftest.py) — pula automaticamente se o banco não
estiver disponível.
"""

import uuid

import psycopg
import pytest
from fastapi.testclient import TestClient

from app.api.app import app
from app.auth.api_keys import create_application


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


def test_create_execution_with_valid_api_key(postgres_dsn, registered_application, client):
    _, api_key = registered_application

    response = client.post(
        "/v1/executions",
        json={"objective": "teste"},
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

    first = client.post("/v1/executions", json={}, headers=headers)
    second = client.post("/v1/executions", json={}, headers=headers)

    assert first.json()["execution_id"] != second.json()["execution_id"]


def test_create_execution_without_api_key_is_rejected(postgres_dsn, client):
    response = client.post("/v1/executions", json={})

    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == 2002


def test_create_execution_with_invalid_api_key_is_rejected(postgres_dsn, client):
    response = client.post(
        "/v1/executions", json={}, headers={"Authorization": "Bearer cldk_naoexiste"}
    )

    assert response.status_code == 401
    assert response.json()["success"] is False
