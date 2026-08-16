"""Teste de integração: escreve de verdade na tabela `logs` do PostgreSQL local
(TASK-006). Requer um PostgreSQL configurado (TASK-003/TASK-004) — pula
automaticamente se as credenciais não estiverem disponíveis nem no ambiente nem em
`config/.env`, para não quebrar a suíte em uma máquina sem esse banco.
"""

import logging
import re
from pathlib import Path

import psycopg
import pytest

from app.observability.postgres_log_handler import (
    attach_postgres_handler,
    build_dsn_from_env,
)

_ENV_FILE = Path(__file__).resolve().parent.parent.parent / "config" / ".env"
_REQUIRED_VARS = (
    "CLAUDIAO_POSTGRES_HOST",
    "CLAUDIAO_POSTGRES_PORT",
    "CLAUDIAO_POSTGRES_DB",
    "CLAUDIAO_POSTGRES_USER",
    "CLAUDIAO_POSTGRES_PASSWORD",
)


def _load_local_env_file(monkeypatch) -> None:
    """Carrega config/.env (não versionado — TASK-003) se as variáveis ainda não
    estiverem no ambiente. Parser simples, só para uso local de teste."""
    if not _ENV_FILE.exists():
        return
    for line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if key in _REQUIRED_VARS:
            monkeypatch.setenv(key, value.strip())


@pytest.fixture
def postgres_dsn(monkeypatch):
    _load_local_env_file(monkeypatch)
    dsn = build_dsn_from_env()
    if dsn is None:
        pytest.skip(
            "Credenciais do PostgreSQL local não disponíveis "
            "(nem no ambiente, nem em config/.env) — pulando teste de integração."
        )
    try:
        with psycopg.connect(dsn, connect_timeout=3):
            pass
    except Exception as exc:
        pytest.skip(f"PostgreSQL local indisponível para o teste de integração: {exc}")
    return dsn


def test_log_record_is_persisted_in_logs_table(postgres_dsn):
    logger = logging.getLogger("claudiao.test.integration")
    logger.handlers.clear()
    logger.setLevel(logging.INFO)
    attached = attach_postgres_handler(logger, dsn=postgres_dsn)
    assert attached is True

    marker = "teste de integração TASK-006 " + re.sub(r"\D", "", str(id(logger)))
    logger.info(marker)

    try:
        with psycopg.connect(postgres_dsn) as conn:
            row = conn.execute(
                "SELECT level, logger, message FROM logs WHERE message = %s",
                (marker,),
            ).fetchone()
            assert row is not None
            level, logger_name, message = row
            assert level == "INFO"
            assert logger_name == "claudiao.test.integration"
            assert message == marker
    finally:
        with psycopg.connect(postgres_dsn) as conn:
            conn.execute("DELETE FROM logs WHERE message = %s", (marker,))
        logger.handlers.clear()
