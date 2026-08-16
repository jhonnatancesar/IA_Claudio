"""Handler de logging que grava registros estruturados no PostgreSQL (TASK-006).

Complementa o logging local em arquivo (TASK-005, `logging_config.py`) — não o
substitui. Uma conexão nova é aberta por mensagem: simples e suficiente para a V1;
um pool de conexões fica para se/quando o volume exigir (não é escopo desta TASK).
Falhas de escrita no banco não derrubam a aplicação nem o logging em arquivo.
"""

from __future__ import annotations

import logging

import psycopg

from app.db.connection import build_dsn_from_env

__all__ = ["PostgresLogHandler", "build_dsn_from_env", "attach_postgres_handler"]


class PostgresLogHandler(logging.Handler):
    """Grava cada `LogRecord` como uma linha na tabela `logs` (docs/DATABASE.md)."""

    def __init__(self, dsn: str) -> None:
        super().__init__()
        self._dsn = dsn

    def emit(self, record: logging.LogRecord) -> None:
        try:
            message = self.format(record)
            with psycopg.connect(self._dsn, connect_timeout=5) as conn:
                conn.execute(
                    "INSERT INTO logs (level, logger, message) VALUES (%s, %s, %s)",
                    (record.levelname, record.name, message),
                )
        except Exception:
            # Nunca deixa uma falha de banco derrubar a aplicação — o logging em
            # arquivo (TASK-005) continua funcionando independentemente disto.
            self.handleError(record)


def attach_postgres_handler(
    logger: logging.Logger, *, dsn: str | None = None
) -> bool:
    """Anexa o `PostgresLogHandler` ao logger, se houver DSN disponível.

    Retorna `True` se o handler foi anexado, `False` se não havia configuração de
    banco disponível — o logging em arquivo continua funcionando normalmente.
    """
    resolved_dsn = dsn if dsn is not None else build_dsn_from_env()
    if not resolved_dsn:
        return False
    handler = PostgresLogHandler(resolved_dsn)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    return True
