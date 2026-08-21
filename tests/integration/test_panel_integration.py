"""Teste de integração: painel web read-only (TASK-081 a TASK-083)
executando de verdade contra o PostgreSQL local, via
`fastapi.testclient.TestClient`. Usa a fixture `postgres_dsn`
(tests/conftest.py) — pula automaticamente se o banco não
estiver disponível.
"""

import uuid

import psycopg
import pytest
from fastapi.testclient import TestClient

from app.api.app import app
from app.auth.api_keys import create_application
from app.observability.execution_trace import ExecutionTrace, save_execution_trace
from app.observability.postgres_log_handler import attach_postgres_handler
from app.queue.queue_model import QueueItem, QueueItemStatus, save_queue_item
from app.usage.usage_model import record_usage


@pytest.fixture(autouse=True)
def cleanup(postgres_dsn):
    yield
    with psycopg.connect(postgres_dsn) as conn:
        conn.execute("DELETE FROM queue_items")
        conn.execute("DELETE FROM execution_traces")
        conn.execute("DELETE FROM logs")
        conn.execute("DELETE FROM applications WHERE name LIKE 'teste_task083_%'")


@pytest.fixture
def client():
    return TestClient(app)


def test_panel_returns_html_page(postgres_dsn, client):
    response = client.get("/panel")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "Claudião — Painel" in response.text


def test_panel_shows_empty_queue_message_when_no_items(postgres_dsn, client):
    response = client.get("/panel")

    assert "Fila vazia." in response.text


def test_panel_lists_real_persisted_queue_items(postgres_dsn, client):
    item = QueueItem.new(payload={"objective": "teste"})
    save_queue_item(item)

    response = client.get("/panel")

    assert item.item_id in response.text
    assert QueueItemStatus.PENDING.value in response.text


def test_panel_shows_empty_executions_message_when_no_traces(postgres_dsn, client):
    response = client.get("/panel")

    assert "Nenhuma execução registrada ainda." in response.text


def test_panel_lists_real_persisted_execution_trace(postgres_dsn, client):
    trace = ExecutionTrace.new(
        execution_id="22222222-2222-2222-2222-222222222222",
        origin="app-teste",
        requester="app-teste",
        objective="buscar o clima de hoje",
    )
    trace.finish(result="resposta pronta")
    save_execution_trace(trace)

    response = client.get("/panel")

    assert trace.execution_id in response.text
    assert "buscar o clima de hoje" in response.text
    assert "resposta pronta" in response.text
    assert "sucesso" in response.text


def test_panel_shows_real_persisted_failed_execution_as_error(postgres_dsn, client):
    trace = ExecutionTrace.new(
        execution_id="88888888-8888-8888-8888-888888888888",
        origin="app-teste",
        requester="app-teste",
        objective="tentar algo que falha",
    )
    trace.finish(result=None)
    save_execution_trace(trace)

    response = client.get("/panel")

    assert "<h2>Erros</h2>" in response.text
    assert "tentar algo que falha" in response.text


def test_panel_shows_empty_logs_message_when_none_persisted(postgres_dsn, client):
    response = client.get("/panel")

    assert "Nenhum log registrado ainda." in response.text


def test_panel_lists_real_persisted_log_entry(postgres_dsn, client):
    import logging

    logger = logging.getLogger("claudiao.teste_task083")
    attach_postgres_handler(logger, dsn=postgres_dsn)
    logger.error("falha real de teste TASK-083")

    response = client.get("/panel")

    assert "falha real de teste TASK-083" in response.text


def test_panel_shows_empty_usage_message_when_none_persisted(postgres_dsn, client):
    response = client.get("/panel")

    assert "Nenhum consumo registrado ainda." in response.text


def test_panel_lists_real_persisted_usage_record(postgres_dsn, client):
    name = f"teste_task083_{uuid.uuid4().hex[:12]}"
    application, _ = create_application(name)
    record_usage(application.id, "99999999-9999-9999-9999-999999999999", "COMPLETED")

    response = client.get("/panel")

    assert "99999999-9999-9999-9999-999999999999" in response.text
    assert str(application.id) in response.text
