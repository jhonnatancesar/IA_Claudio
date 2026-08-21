"""Teste de integração: painel web read-only (TASK-081) executando de
verdade contra o PostgreSQL local, via `fastapi.testclient.TestClient`.
Usa a fixture `postgres_dsn` (tests/integration/conftest.py) — pula
automaticamente se o banco não estiver disponível.
"""

import psycopg
import pytest
from fastapi.testclient import TestClient

from app.api.app import app
from app.queue.queue_model import QueueItem, QueueItemStatus, save_queue_item


@pytest.fixture(autouse=True)
def cleanup(postgres_dsn):
    yield
    with psycopg.connect(postgres_dsn) as conn:
        conn.execute("DELETE FROM queue_items")


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
