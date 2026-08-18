"""Modelo de memória persistente (TASK-044).

Seção 11 da especificação mestre (`docs/MEMORY.md`): memória persistente
armazena preferências, decisões, fatos pessoais úteis, histórico importante
e informações necessárias à continuidade — separada de contexto imediato
(`app.context`, TASK-037+) e de conhecimento (TASK-052+).

Schema em `backend/app/db/migrations/0003_memory.sql`: tabela `memories`
com `owner_type`/`owner_id` já presentes (escopos mínimos `USER`/
`APPLICATION`, seção 11), mas garantir que uma consulta só devolve
memórias do próprio dono é TASK-045, não implementado aqui — esta TASK só
cria e lê uma memória pelo `id`, sem filtrar por dono.

Relevância/frequência/last_used (TASK-048), política de retenção
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
