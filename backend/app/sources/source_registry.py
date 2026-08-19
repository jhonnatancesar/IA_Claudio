"""Cadastro de fontes (TASK-059).

Seções 14/15 da especificação mestre (`docs/TRUST_GUARDRAILS.md`, "Fontes
e reputação"): o sistema mantém uma base de fontes para avaliar
reputação e decidir confiabilidade de evidências. Esta TASK cria só a
identidade da fonte — `identifier` (URL/domínio) e `id` — para as TASKs
seguintes se apoiarem: tipo `PRIMARY`/`SECONDARY`/`UNKNOWN` (TASK-060),
reputação `LOW`/`MEDIUM`/`HIGH` (TASK-061), atualização de reputação
(TASK-062), histórico de reputação (TASK-063), blacklist (TASK-064),
bloqueio automático (TASK-065) e desbloqueio só por `ADMIN` (TASK-066)
não são desta TASK.

`register_source` é idempotente por `identifier` (`UNIQUE` no schema,
`backend/app/db/migrations/0010_sources.sql`): registrar a mesma fonte
duas vezes reaproveita o cadastro existente, nunca duplica — mesma fonte
pesquisada de novo não vira uma entidade nova sem reputação.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.db.connection import connect


@dataclass(frozen=True)
class Source:
    id: UUID
    identifier: str
    created_at: datetime


def register_source(identifier: str) -> Source:
    """Registra uma fonte pelo seu `identifier` (URL/domínio). Se já
    existir uma fonte com esse `identifier`, devolve a existente em vez
    de criar outra. Levanta `ValueError` para `identifier` vazio."""
    if not identifier or not identifier.strip():
        raise ValueError("identifier não pode ser vazio")

    with connect() as conn:
        row = conn.execute(
            "INSERT INTO sources (identifier) VALUES (%s) "
            "ON CONFLICT (identifier) DO UPDATE SET identifier = EXCLUDED.identifier "
            "RETURNING id, identifier, created_at",
            (identifier,),
        ).fetchone()

    source_id, source_identifier, created_at = row
    return Source(id=source_id, identifier=source_identifier, created_at=created_at)


def get_source(source_id: UUID) -> Source | None:
    """Busca uma fonte pelo `id`. Retorna `None` se não existir."""
    with connect() as conn:
        row = conn.execute(
            "SELECT id, identifier, created_at FROM sources WHERE id = %s",
            (source_id,),
        ).fetchone()

    if row is None:
        return None
    source_id, identifier, created_at = row
    return Source(id=source_id, identifier=identifier, created_at=created_at)


def get_source_by_identifier(identifier: str) -> Source | None:
    """Busca uma fonte pelo `identifier` (URL/domínio). Retorna `None` se
    não existir."""
    with connect() as conn:
        row = conn.execute(
            "SELECT id, identifier, created_at FROM sources WHERE identifier = %s",
            (identifier,),
        ).fetchone()

    if row is None:
        return None
    source_id, source_identifier, created_at = row
    return Source(id=source_id, identifier=source_identifier, created_at=created_at)
