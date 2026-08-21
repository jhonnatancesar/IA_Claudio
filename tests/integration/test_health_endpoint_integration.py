"""Teste de integração: `GET /health` (TASK-085) real, via
`fastapi.testclient.TestClient`, e o `run_health_check` chamado de
verdade no evento de inicialização do FastAPI (`lifespan`,
`app.api.app`). Usa a fixture `postgres_dsn`
(tests/conftest.py) — pula automaticamente se o banco não
estiver disponível.
"""

import pytest
from fastapi.testclient import TestClient

from app.api.app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_endpoint_returns_json_with_checks(postgres_dsn, client):
    response = client.get("/health")

    body = response.json()
    assert "healthy" in body
    assert isinstance(body["checks"], list)
    names = {check["name"] for check in body["checks"]}
    assert names == {
        "modelo/runtime",
        "postgresql",
        "fila",
        "ferramentas/providers principais",
        "configurações críticas",
    }


def test_health_endpoint_returns_503_when_critical_config_missing(
    postgres_dsn, client, monkeypatch
):
    monkeypatch.delenv("CLAUDIAO_ACTIVE_MODEL", raising=False)
    monkeypatch.delenv("CLAUDIAO_MASTER_KEY_PATH", raising=False)

    response = client.get("/health")

    assert response.status_code == 503
    assert response.json()["healthy"] is False


def test_health_endpoint_returns_200_when_everything_configured(
    postgres_dsn, client, monkeypatch, tmp_path
):
    monkeypatch.setenv("CLAUDIAO_ACTIVE_MODEL", "modelo-de-teste")
    monkeypatch.setenv("CLAUDIAO_MASTER_KEY_PATH", str(tmp_path / "master.key"))

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["healthy"] is True


def test_lifespan_startup_runs_health_check_and_logs_result(postgres_dsn, caplog):
    """`with TestClient(app) as _client` dispara o `lifespan` (startup/
    shutdown) de verdade — confirma que `run_health_check()` roda no
    evento de inicialização e que o resultado é mesmo registrado via
    `logging` (`caplog`, biblioteca padrão de teste — mais confiável do
    que checar a tabela `logs` do PostgreSQL aqui: o handler do
    PostgreSQL só é anexado se `CLAUDIAO_POSTGRES_*` já estiver no
    ambiente no primeiro `get_logger()` do processo, o que a ordem de
    coleta do pytest não garante — lacuna pré-existente de
    `logging_config.py`, TASK-005, não desta TASK)."""
    with caplog.at_level("INFO", logger="claudiao.health_check"):
        with TestClient(app) as _client:
            pass  # __enter__/__exit__ disparam o lifespan (startup/shutdown)

    messages = [record.message for record in caplog.records]
    assert any(message.startswith("health check:") for message in messages)
