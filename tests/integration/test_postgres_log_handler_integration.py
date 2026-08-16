"""Teste de integração: escreve de verdade na tabela `logs` do PostgreSQL local
(TASK-006). Requer um PostgreSQL configurado (TASK-003/TASK-004) — a fixture
`postgres_dsn` (tests/integration/conftest.py) pula automaticamente se as
credenciais não estiverem disponíveis nem no ambiente nem em `config/.env`.
"""

import logging
import re

import psycopg

from app.observability.postgres_log_handler import attach_postgres_handler


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
