"""Handler de logging que grava registros estruturados no PostgreSQL (TASK-006).

Complementa o logging local em arquivo (TASK-005, `logging_config.py`) — não o
substitui. Uma conexão nova é aberta por mensagem: simples e suficiente para a V1;
um pool de conexões fica para se/quando o volume exigir (não é escopo desta TASK).
Falhas de escrita no banco não derrubam a aplicação nem o logging em arquivo.

Esta TASK (TASK-083) acrescenta `list_recent_logs`: leitura da tabela
`logs`, para o painel (`app.panel.routes`, "logs recentes",
`docs/PANEL.md`) mostrar linhas reais. Lacuna conhecida, registrada aqui
para não parecer esquecida: nenhum módulo da aplicação (orquestrador,
API, guardrails) chama `logger.error`/`logger.warning` em nenhum ponto
real hoje — `get_logger`/`PostgresLogHandler` só são exercitados pelos
próprios testes de observabilidade. Na prática, `list_recent_logs`
provavelmente devolve uma lista vazia até alguma TASK futura passar a
logar eventos de verdade durante uma execução/erro.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime

import psycopg

from app.db.connection import build_dsn_from_env, connect

__all__ = [
    "PostgresLogHandler",
    "build_dsn_from_env",
    "attach_postgres_handler",
    "LogEntry",
    "list_recent_logs",
]


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


@dataclass(frozen=True)
class LogEntry:
    id: int
    timestamp: datetime
    level: str
    logger: str
    message: str


def list_recent_logs(limit: int = 50) -> list[LogEntry]:
    """Lista as linhas mais recentes de `logs`, mais nova primeiro
    (TASK-083) — até `limit` (padrão 50, painel read-only, não
    exportação completa)."""
    with connect() as conn:
        rows = conn.execute(
            'SELECT id, "timestamp", level, logger, message FROM logs '
            'ORDER BY "timestamp" DESC LIMIT %s',
            (limit,),
        ).fetchall()

    return [
        LogEntry(id=row[0], timestamp=row[1], level=row[2], logger=row[3], message=row[4])
        for row in rows
    ]
