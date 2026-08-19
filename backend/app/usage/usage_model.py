"""Rastreio de consumo por aplicação (TASK-073).

Seção 28 da especificação mestre (`docs/QUOTAS.md`): a V1 controla cota
por usuário/API key, medindo tokens/processamento, número de requisições
e volume de dados. Medição de verdade (tokens/volume), ciclo de renovação,
avisos em 80%/95% e bloqueio em 100% são o sistema de cotas completo —
TASK-108 a TASK-114, não implementados aqui.

Esta TASK só grava o registro mínimo de que uma requisição aconteceu: uma
linha por execução processada por `POST /v1/executions`
(`backend/app/api/executions.py`), identificando a aplicação
(`application_id`), a execução (`execution_id` — texto, não FK, porque
`Execution` ainda não é persistida em tabela própria; isso é a
fila/observabilidade, TASK-074 em diante) e o status final. É a base sobre
a qual o sistema de cotas completo mede/agrega depois — "número de
requisições" já é coberto por `COUNT(*)`; tokens/volume ainda não têm
onde ser gravados (não fazem parte desta TASK).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.db.connection import connect

_SELECT_COLUMNS = "id, application_id, execution_id, status, created_at"


@dataclass(frozen=True)
class UsageRecord:
    id: UUID
    application_id: UUID
    execution_id: str
    status: str
    created_at: datetime


def _usage_record_from_row(row: tuple) -> UsageRecord:
    record_id, application_id, execution_id, status, created_at = row
    return UsageRecord(
        id=record_id,
        application_id=application_id,
        execution_id=execution_id,
        status=status,
        created_at=created_at,
    )


def record_usage(application_id: UUID, execution_id: str, status: str) -> UsageRecord:
    """Grava uma linha de consumo: `application_id` fez uma requisição que
    resultou na execução `execution_id`, terminada com `status` (o valor
    de `Execution.status`, ex. `COMPLETED`/`FAILED`/`CANCELLED` — texto
    livre aqui, sem `CHECK`, porque quem chama já validou contra
    `ExecutionStatus`)."""
    with connect() as conn:
        row = conn.execute(
            "INSERT INTO usage_records (application_id, execution_id, status) "
            f"VALUES (%s, %s, %s) RETURNING {_SELECT_COLUMNS}",
            (application_id, execution_id, status),
        ).fetchone()

    return _usage_record_from_row(row)


def list_usage_for_application(application_id: UUID) -> list[UsageRecord]:
    """Lista o consumo registrado de uma aplicação, do mais antigo para o
    mais recente (`created_at` crescente)."""
    with connect() as conn:
        rows = conn.execute(
            f"SELECT {_SELECT_COLUMNS} FROM usage_records "
            "WHERE application_id = %s ORDER BY created_at ASC",
            (application_id,),
        ).fetchall()

    return [_usage_record_from_row(row) for row in rows]
