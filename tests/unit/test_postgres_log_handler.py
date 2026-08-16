"""Testes unitários do handler de logging estruturado no PostgreSQL (TASK-006).

Sem tocar banco real aqui — isso é coberto pelo teste de integração em
tests/integration/test_postgres_log_handler_integration.py. Aqui cobrimos só a
lógica que não depende de uma conexão de verdade: montagem de DSN a partir do
ambiente e o comportamento de "anexar só se houver configuração".
"""

import logging

import pytest

from app.observability.postgres_log_handler import (
    PostgresLogHandler,
    attach_postgres_handler,
    build_dsn_from_env,
)

_ALL_VARS = (
    "CLAUDIAO_POSTGRES_HOST",
    "CLAUDIAO_POSTGRES_PORT",
    "CLAUDIAO_POSTGRES_DB",
    "CLAUDIAO_POSTGRES_USER",
    "CLAUDIAO_POSTGRES_PASSWORD",
)


@pytest.fixture(autouse=True)
def _clear_postgres_env(monkeypatch):
    for var in _ALL_VARS:
        monkeypatch.delenv(var, raising=False)


def test_build_dsn_returns_none_when_env_incomplete(monkeypatch):
    monkeypatch.setenv("CLAUDIAO_POSTGRES_HOST", "127.0.0.1")
    # Faltam as demais variáveis obrigatórias.
    assert build_dsn_from_env() is None


def test_build_dsn_builds_dsn_when_env_complete(monkeypatch):
    monkeypatch.setenv("CLAUDIAO_POSTGRES_HOST", "127.0.0.1")
    monkeypatch.setenv("CLAUDIAO_POSTGRES_PORT", "5432")
    monkeypatch.setenv("CLAUDIAO_POSTGRES_DB", "claudiao")
    monkeypatch.setenv("CLAUDIAO_POSTGRES_USER", "claudiao_app")
    monkeypatch.setenv("CLAUDIAO_POSTGRES_PASSWORD", "segredo")

    dsn = build_dsn_from_env()

    assert dsn is not None
    assert "host=127.0.0.1" in dsn
    assert "port=5432" in dsn
    assert "dbname=claudiao" in dsn
    assert "user=claudiao_app" in dsn
    assert "password=segredo" in dsn


def test_attach_postgres_handler_returns_false_without_config():
    logger = logging.getLogger("claudiao.test.no-db")
    logger.handlers.clear()

    attached = attach_postgres_handler(logger)

    assert attached is False
    assert logger.handlers == []


def test_attach_postgres_handler_attaches_when_dsn_given():
    logger = logging.getLogger("claudiao.test.with-dsn")
    logger.handlers.clear()

    attached = attach_postgres_handler(logger, dsn="host=127.0.0.1 dbname=x user=y password=z")

    assert attached is True
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], PostgresLogHandler)
    logger.handlers.clear()


def test_emit_never_raises_on_connection_failure():
    """Uma DSN inválida não pode derrubar a aplicação — só falha silenciosamente
    (via logging.Handler.handleError), preservando o logging em arquivo (TASK-005)."""
    # 192.0.2.1 é endereço reservado para documentação/teste (RFC 5737, TEST-NET-1),
    # nunca roteável — falha rápido por timeout, sem depender de resolução DNS.
    handler = PostgresLogHandler(dsn="host=192.0.2.1 connect_timeout=1")
    handler.setFormatter(logging.Formatter("%(message)s"))
    record = logging.LogRecord(
        name="claudiao.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="não deve lançar exceção",
        args=(),
        exc_info=None,
    )

    handler.emit(record)  # não deve levantar
