"""Modelo de memória persistente (TASK-044).

Seção 11 da especificação mestre (`docs/MEMORY.md`): memória persistente
armazena preferências, decisões, fatos pessoais úteis, histórico importante
e informações necessárias à continuidade — separada de contexto imediato
(`app.context`, TASK-037+) e de conhecimento (TASK-052+).

Schema em `backend/app/db/migrations/0003_memory.sql`: tabela `memories`
com `owner_type`/`owner_id` já presentes (escopos mínimos `USER`/
`APPLICATION`, seção 11). TASK-044 só criava e lia uma memória pelo `id`,
sem filtrar por dono — esta TASK (TASK-045) acrescenta
`list_memories_for_owner`, a garantia de fato de que uma consulta só
devolve memórias do próprio dono ("usuários diferentes têm memórias
separadas", seção 11): filtra por `owner_type`/`owner_id` exatos, nunca
retorna memórias de outro dono.

Memory Tool (TASK-046), busca estruturada (TASK-047),
relevância/frequência/last_used (TASK-048), política de retenção
(TASK-049), limite fixo (TASK-050) e auditoria de remoção (TASK-051) não
são desta TASK.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.db.connection import connect

VALID_OWNER_TYPES = ("USER", "APPLICATION")


class InvalidOwnerTypeError(ValueError):
    """Levantado quando `owner_type` não é `USER` nem `APPLICATION`."""


@dataclass(frozen=True)
class Memory:
    id: UUID
    owner_type: str
    owner_id: str
    content: str
    created_at: datetime


def save_memory(owner_type: str, owner_id: str, content: str) -> Memory:
    """Persiste uma memória nova. Levanta `InvalidOwnerTypeError` para
    `owner_type` desconhecido e `ValueError` para `owner_id`/`content`
    vazios."""
    if owner_type not in VALID_OWNER_TYPES:
        raise InvalidOwnerTypeError(f"owner_type inválido: {owner_type!r}")
    if not owner_id or not owner_id.strip():
        raise ValueError("owner_id não pode ser vazio")
    if not content or not content.strip():
        raise ValueError("content não pode ser vazio")

    with connect() as conn:
        row = conn.execute(
            "INSERT INTO memories (owner_type, owner_id, content) "
            "VALUES (%s, %s, %s) "
            "RETURNING id, owner_type, owner_id, content, created_at",
            (owner_type, owner_id, content),
        ).fetchone()

    memory_id, db_owner_type, db_owner_id, db_content, created_at = row
    return Memory(
        id=memory_id,
        owner_type=db_owner_type,
        owner_id=db_owner_id,
        content=db_content,
        created_at=created_at,
    )


def get_memory(memory_id: UUID) -> Memory | None:
    """Busca uma memória pelo `id`. Retorna `None` se não existir."""
    with connect() as conn:
        row = conn.execute(
            "SELECT id, owner_type, owner_id, content, created_at "
            "FROM memories WHERE id = %s",
            (memory_id,),
        ).fetchone()

    if row is None:
        return None
    memory_id, owner_type, owner_id, content, created_at = row
    return Memory(
        id=memory_id,
        owner_type=owner_type,
        owner_id=owner_id,
        content=content,
        created_at=created_at,
    )


def list_memories_for_owner(owner_type: str, owner_id: str) -> list[Memory]:
    """Lista todas as memórias de um dono específico (TASK-045) — nunca
    devolve memórias de outro `owner_type`/`owner_id`, mesmo que existam
    muitas na tabela. Ordem: mais recente primeiro (`created_at DESC`).
    Levanta `InvalidOwnerTypeError` para `owner_type` desconhecido."""
    if owner_type not in VALID_OWNER_TYPES:
        raise InvalidOwnerTypeError(f"owner_type inválido: {owner_type!r}")

    with connect() as conn:
        rows = conn.execute(
            "SELECT id, owner_type, owner_id, content, created_at "
            "FROM memories WHERE owner_type = %s AND owner_id = %s "
            "ORDER BY created_at DESC",
            (owner_type, owner_id),
        ).fetchall()

    return [
        Memory(
            id=row[0],
            owner_type=row[1],
            owner_id=row[2],
            content=row[3],
            created_at=row[4],
        )
        for row in rows
    ]
