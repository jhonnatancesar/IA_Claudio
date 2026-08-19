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

Esta TASK (TASK-060) acrescenta `SourceType`
(`PRIMARY`/`SECONDARY`/`UNKNOWN`, seção 14/15: "fonte primária/oficial
forte pode bastar sozinha... fontes secundárias podem exigir múltiplas
fontes independentes"). `UNKNOWN` por padrão — uma fonte recém-registrada
ainda não foi classificada. `set_source_type` reclassifica uma fonte já
existente. Reputação (TASK-061 em diante) é um conceito separado do
tipo — uma fonte `PRIMARY` não é automaticamente `HIGH`.

Esta TASK (TASK-061) acrescenta `SourceReputation`
(`LOW`/`MEDIUM`/`HIGH`, seção 14/15: "Confiabilidade: LOW / MEDIUM /
HIGH"). `MEDIUM` por padrão — uma fonte sem histórico ainda não merece
confiança alta nem baixa, e `MEDIUM` já implica aviso ao ser usada
(comportamento conservador correto para algo não avaliado).
`set_source_reputation` só aplica a troca *mecânica* de reputação — a
regra de negócio que decide *quando* rebaixar/elevar com base em dados
corretos/errados apresentados é atualização de reputação, TASK-062, não
implementada aqui.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from app.db.connection import connect

_SELECT_COLUMNS = "id, identifier, created_at, source_type, reputation"


class SourceType(StrEnum):
    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"
    UNKNOWN = "UNKNOWN"


class SourceReputation(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class SourceNotFoundError(ValueError):
    """Levantado quando um `source_id` não corresponde a nenhuma fonte
    existente."""


@dataclass(frozen=True)
class Source:
    id: UUID
    identifier: str
    created_at: datetime
    source_type: SourceType
    reputation: SourceReputation


def _source_from_row(row: tuple) -> Source:
    source_id, identifier, created_at, source_type, reputation = row
    return Source(
        id=source_id,
        identifier=identifier,
        created_at=created_at,
        source_type=SourceType(source_type),
        reputation=SourceReputation(reputation),
    )


def register_source(
    identifier: str,
    source_type: SourceType = SourceType.UNKNOWN,
    reputation: SourceReputation = SourceReputation.MEDIUM,
) -> Source:
    """Registra uma fonte pelo seu `identifier` (URL/domínio). Se já
    existir uma fonte com esse `identifier`, devolve a existente em vez
    de criar outra (`source_type`/`reputation` só se aplicam ao criar;
    não alteram uma fonte já registrada — use `set_source_type`/
    `set_source_reputation` para isso). Levanta `ValueError` para
    `identifier` vazio."""
    if not identifier or not identifier.strip():
        raise ValueError("identifier não pode ser vazio")

    with connect() as conn:
        row = conn.execute(
            "INSERT INTO sources (identifier, source_type, reputation) "
            "VALUES (%s, %s, %s) "
            "ON CONFLICT (identifier) DO UPDATE SET identifier = EXCLUDED.identifier "
            f"RETURNING {_SELECT_COLUMNS}",
            (identifier, source_type.value, reputation.value),
        ).fetchone()

    return _source_from_row(row)


def get_source(source_id: UUID) -> Source | None:
    """Busca uma fonte pelo `id`. Retorna `None` se não existir."""
    with connect() as conn:
        row = conn.execute(
            f"SELECT {_SELECT_COLUMNS} FROM sources WHERE id = %s",
            (source_id,),
        ).fetchone()

    if row is None:
        return None
    return _source_from_row(row)


def get_source_by_identifier(identifier: str) -> Source | None:
    """Busca uma fonte pelo `identifier` (URL/domínio). Retorna `None` se
    não existir."""
    with connect() as conn:
        row = conn.execute(
            f"SELECT {_SELECT_COLUMNS} FROM sources WHERE identifier = %s",
            (identifier,),
        ).fetchone()

    if row is None:
        return None
    return _source_from_row(row)


def set_source_type(source_id: UUID, source_type: SourceType) -> Source:
    """Reclassifica uma fonte já registrada (TASK-060). Levanta
    `SourceNotFoundError` se `source_id` não existir."""
    with connect() as conn:
        row = conn.execute(
            "UPDATE sources SET source_type = %s WHERE id = %s "
            f"RETURNING {_SELECT_COLUMNS}",
            (source_type.value, source_id),
        ).fetchone()

    if row is None:
        raise SourceNotFoundError(f"fonte não encontrada: {source_id!r}")
    return _source_from_row(row)


def set_source_reputation(source_id: UUID, reputation: SourceReputation) -> Source:
    """Aplica a troca mecânica de reputação de uma fonte já registrada
    (TASK-061) — sem decidir se a troca é apropriada, isso é a regra de
    atualização de reputação, TASK-062. Levanta `SourceNotFoundError` se
    `source_id` não existir."""
    with connect() as conn:
        row = conn.execute(
            "UPDATE sources SET reputation = %s WHERE id = %s "
            f"RETURNING {_SELECT_COLUMNS}",
            (reputation.value, source_id),
        ).fetchone()

    if row is None:
        raise SourceNotFoundError(f"fonte não encontrada: {source_id!r}")
    return _source_from_row(row)
