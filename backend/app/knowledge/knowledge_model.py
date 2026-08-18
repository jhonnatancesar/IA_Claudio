"""Modelo RAW/PROVISIONAL/CONFIRMED de conhecimento (TASK-052).

Seção 12 da especificação mestre (`docs/KNOWLEDGE.md`): conhecimento é
**separado da memória** (`app.memory`, TASK-044+) e **nunca é apagado
automaticamente** — por isso este módulo não tem uma função de remoção,
diferente de `app.memory.memory_model`. Ciclo de maturidade: "fluxo
desejado: NÃO SEI → PESQUISO → VALIDO → CONFIRMO → AVALIO UTILIDADE →
SALVO", formalizado aqui como `RAW → PROVISIONAL → CONFIRMED`.

Esta TASK cria o modelo de dados e a transição *mecânica* entre estágios —
mesmo padrão de `Execution` (TASK-020): estados válidos e um grafo de
transições permitidas (um passo por vez, sempre para frente, nunca
pulando nem voltando), sem decidir *quando* uma transição deve acontecer.
A regra de negócio que decide quando promover para `CONFIRMED` (baseada em
evidências/fontes) é TASK-057, não implementada aqui —
`advance_knowledge_status` só aplica a transição que quem chama já
decidiu que deve acontecer.

Versionamento (TASK-054), escopo `GLOBAL`/`APPLICATION` (TASK-055),
evidências/fontes (TASK-056) e avaliação de utilidade pelo orquestrador
(TASK-058) também não são desta TASK — `content` é só texto simples por
ora.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from app.db.connection import connect


class KnowledgeStatus(StrEnum):
    RAW = "RAW"
    PROVISIONAL = "PROVISIONAL"
    CONFIRMED = "CONFIRMED"


_VALID_TRANSITIONS: dict[KnowledgeStatus, frozenset[KnowledgeStatus]] = {
    KnowledgeStatus.RAW: frozenset({KnowledgeStatus.PROVISIONAL}),
    KnowledgeStatus.PROVISIONAL: frozenset({KnowledgeStatus.CONFIRMED}),
    KnowledgeStatus.CONFIRMED: frozenset(),
}
"""Grafo de transições válidas: só para frente, um passo por vez.
`CONFIRMED` não tem saída aqui — reverter uma confirmação é versionamento
(TASK-054), não uma transição de status."""


class KnowledgeNotFoundError(ValueError):
    """Levantado quando um `knowledge_id` não corresponde a nenhum
    conhecimento existente."""


class InvalidKnowledgeStatusTransitionError(ValueError):
    """Levantado ao tentar uma transição de status fora do grafo
    `RAW → PROVISIONAL → CONFIRMED`."""


@dataclass(frozen=True)
class Knowledge:
    id: UUID
    status: KnowledgeStatus
    content: str
    created_at: datetime


def _knowledge_from_row(row: tuple[Any, ...]) -> Knowledge:
    knowledge_id, status, content, created_at = row
    return Knowledge(
        id=knowledge_id,
        status=KnowledgeStatus(status),
        content=content,
        created_at=created_at,
    )


def save_knowledge(content: str) -> Knowledge:
    """Persiste um fato novo, sempre começando em `RAW` ("NÃO SEI" — a
    primeira captura, antes de qualquer validação). Levanta `ValueError`
    para `content` vazio."""
    if not content or not content.strip():
        raise ValueError("content não pode ser vazio")

    with connect() as conn:
        row = conn.execute(
            "INSERT INTO knowledge (content) VALUES (%s) "
            "RETURNING id, status, content, created_at",
            (content,),
        ).fetchone()

    return _knowledge_from_row(row)


def get_knowledge(knowledge_id: UUID) -> Knowledge | None:
    """Busca um conhecimento pelo `id`. Retorna `None` se não existir."""
    with connect() as conn:
        row = conn.execute(
            "SELECT id, status, content, created_at FROM knowledge WHERE id = %s",
            (knowledge_id,),
        ).fetchone()

    if row is None:
        return None
    return _knowledge_from_row(row)


def advance_knowledge_status(
    knowledge_id: UUID, new_status: KnowledgeStatus
) -> Knowledge:
    """Aplica uma transição mecânica de status: `RAW → PROVISIONAL →
    CONFIRMED`, um passo por vez. Levanta `KnowledgeNotFoundError` se
    `knowledge_id` não existir, e `InvalidKnowledgeStatusTransitionError`
    se `new_status` não for um destino válido a partir do status atual
    (isso inclui pular etapa, voltar, ou repetir o mesmo status).

    Decidir *quando* uma transição deve acontecer (com base em
    evidências/fontes) é TASK-057 — esta função só valida e aplica."""
    knowledge = get_knowledge(knowledge_id)
    if knowledge is None:
        raise KnowledgeNotFoundError(f"conhecimento não encontrado: {knowledge_id!r}")

    if new_status not in _VALID_TRANSITIONS[knowledge.status]:
        raise InvalidKnowledgeStatusTransitionError(
            f"transição inválida: {knowledge.status} -> {new_status}"
        )

    with connect() as conn:
        row = conn.execute(
            "UPDATE knowledge SET status = %s, updated_at = now() WHERE id = %s "
            "RETURNING id, status, content, created_at",
            (new_status.value, knowledge_id),
        ).fetchone()

    return _knowledge_from_row(row)
