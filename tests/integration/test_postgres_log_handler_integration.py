"""Teste de integração: escreve de verdade na tabela `logs` do PostgreSQL local
(TASK-006). Requer um PostgreSQL configurado (TASK-003/TASK-004) — a fixture
`postgres_dsn` (tests/conftest.py) pula automaticamente se as
credenciais não estiverem disponíveis nem no ambiente nem em `config/.env`.
"""

import logging
import re

import psycopg

from app.observability.postgres_log_handler import attach_postgres_handler, list_recent_logs


def test_log_record_is_persisted_in_logs_table(postgres_dsn):
    logger = logging.getLogger("claudiao.test.integration")
    logger.handlers.clear()
    logger.setLevel(logging.INFO)
    logger.propagate = False
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


def test_list_recent_logs_reads_real_persisted_entry(postgres_dsn):
    logger = logging.getLogger("claudiao.test.integration.list")
    logger.handlers.clear()
    logger.setLevel(logging.INFO)
    logger.propagate = False
    attach_postgres_handler(logger, dsn=postgres_dsn)

    marker = "teste TASK-083 list_recent_logs " + re.sub(r"\D", "", str(id(logger)))
    logger.warning(marker)

    try:
        entries = list_recent_logs(limit=50)
        matching = [entry for entry in entries if entry.message == marker]
        assert len(matching) == 1
        assert matching[0].level == "WARNING"
        assert matching[0].logger == "claudiao.test.integration.list"
    finally:
        with psycopg.connect(postgres_dsn) as conn:
            conn.execute("DELETE FROM logs WHERE message = %s", (marker,))
        logger.handlers.clear()


def test_list_recent_logs_respects_limit(postgres_dsn):
    assert len(list_recent_logs(limit=1)) <= 1
