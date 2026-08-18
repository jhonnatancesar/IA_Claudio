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

Memory Tool (TASK-046) expõe as funções deste módulo ao protocolo do
orquestrador (`app.tools.memory_tool`). TASK-047 acrescentou
`search_memories`: busca estruturada por conteúdo, dentro do escopo de um
dono (reaproveita a garantia de separação da TASK-045) — combinação
`owner_type`/`owner_id`/`query`, sem ranking por relevância.

Esta TASK (TASK-048) acrescenta rastreamento de uso: `use_count`
(frequência) e `last_used_at` (last used), colunas novas em
`backend/app/db/migrations/0004_memory_usage.sql`. `record_memory_usage`
incrementa `use_count` e atualiza `last_used_at` — "se voltar a ser usada
antes da limpeza, a vida útil é renovada" (seção 11) depende de
`last_used_at` estar atualizado, mas a limpeza de fato é TASK-049, não
aqui. `relevance_score` combina os dois numa pontuação heurística — a
especificação lista "relevância" e "pouco uso" como critérios de limpeza
sem detalhar uma fórmula, então o critério aqui é o mais simples e
defensável possível (mesmo espírito do threshold de `loop_detector.py`,
TASK-029).

Política de retenção (TASK-049, `app.memory.retention_policy`), limite
fixo (TASK-050) e auditoria de remoção (TASK-051) não são deste módulo.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.db.connection import connect

VALID_OWNER_TYPES = ("USER", "APPLICATION")


class InvalidOwnerTypeError(ValueError):
    """Levantado quando `owner_type` não é `USER` nem `APPLICATION`."""


class MemoryNotFoundError(ValueError):
    """Levantado quando um `memory_id` não corresponde a nenhuma memória
    existente."""


@dataclass(frozen=True)
class Memory:
    id: UUID
    owner_type: str
    owner_id: str
    content: str
    created_at: datetime
    use_count: int = 0
    last_used_at: datetime | None = None


def _memory_from_row(row: tuple) -> Memory:
    memory_id, owner_type, owner_id, content, created_at, use_count, last_used_at = row
    return Memory(
        id=memory_id,
        owner_type=owner_type,
        owner_id=owner_id,
        content=content,
        created_at=created_at,
        use_count=use_count,
        last_used_at=last_used_at,
    )


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
            "RETURNING id, owner_type, owner_id, content, created_at, "
            "use_count, last_used_at",
            (owner_type, owner_id, content),
        ).fetchone()

    return _memory_from_row(row)


def get_memory(memory_id: UUID) -> Memory | None:
    """Busca uma memória pelo `id`. Retorna `None` se não existir."""
    with connect() as conn:
        row = conn.execute(
            "SELECT id, owner_type, owner_id, content, created_at, "
            "use_count, last_used_at "
            "FROM memories WHERE id = %s",
            (memory_id,),
        ).fetchone()

    if row is None:
        return None
    return _memory_from_row(row)


def list_memories_for_owner(owner_type: str, owner_id: str) -> list[Memory]:
    """Lista todas as memórias de um dono específico (TASK-045) — nunca
    devolve memórias de outro `owner_type`/`owner_id`, mesmo que existam
    muitas na tabela. Ordem: mais recente primeiro (`created_at DESC`).
    Levanta `InvalidOwnerTypeError` para `owner_type` desconhecido."""
    if owner_type not in VALID_OWNER_TYPES:
        raise InvalidOwnerTypeError(f"owner_type inválido: {owner_type!r}")

    with connect() as conn:
        rows = conn.execute(
            "SELECT id, owner_type, owner_id, content, created_at, "
            "use_count, last_used_at "
            "FROM memories WHERE owner_type = %s AND owner_id = %s "
            "ORDER BY created_at DESC",
            (owner_type, owner_id),
        ).fetchall()

    return [_memory_from_row(row) for row in rows]


def search_memories(owner_type: str, owner_id: str, query: str) -> list[Memory]:
    """Busca estruturada por conteúdo (TASK-047): memórias de
    `owner_type`/`owner_id` cujo `content` contém `query` (comparação sem
    diferenciar maiúsculas/minúsculas), mais recente primeiro. Nunca
    devolve memórias de outro dono — mesma garantia de
    `list_memories_for_owner` (TASK-045). Sem ranking por relevância
    (TASK-048). Levanta `InvalidOwnerTypeError` para `owner_type`
    desconhecido e `ValueError` para `query` vazia."""
    if owner_type not in VALID_OWNER_TYPES:
        raise InvalidOwnerTypeError(f"owner_type inválido: {owner_type!r}")
    if not query or not query.strip():
        raise ValueError("query não pode ser vazia")

    with connect() as conn:
        rows = conn.execute(
            "SELECT id, owner_type, owner_id, content, created_at, "
            "use_count, last_used_at "
            "FROM memories "
            "WHERE owner_type = %s AND owner_id = %s AND content ILIKE %s "
            "ORDER BY created_at DESC",
            (owner_type, owner_id, f"%{query}%"),
        ).fetchall()

    return [_memory_from_row(row) for row in rows]


def record_memory_usage(memory_id: UUID) -> Memory:
    """Registra um uso da memória `memory_id` (TASK-048): incrementa
    `use_count` e atualiza `last_used_at` para agora. Levanta
    `MemoryNotFoundError` se `memory_id` não existir."""
    with connect() as conn:
        row = conn.execute(
            "UPDATE memories SET use_count = use_count + 1, last_used_at = now() "
            "WHERE id = %s "
            "RETURNING id, owner_type, owner_id, content, created_at, "
            "use_count, last_used_at",
            (memory_id,),
        ).fetchone()

    if row is None:
        raise MemoryNotFoundError(f"memória não encontrada: {memory_id!r}")
    return _memory_from_row(row)


def delete_memory(memory_id: UUID) -> bool:
    """Remove a memória `memory_id` (TASK-049, usado por
    `app.memory.retention_policy`). Retorna `True` se algo foi removido,
    `False` se `memory_id` já não existia. Sem auditoria da remoção —
    isso é TASK-051, não implementado aqui."""
    with connect() as conn:
        result = conn.execute("DELETE FROM memories WHERE id = %s", (memory_id,))
    return result.rowcount > 0


def relevance_score(memory: Memory, now: datetime) -> float:
    """Pontuação heurística de relevância (TASK-048), combinando frequência
    de uso (`use_count`) e recência (`last_used_at`, ou `created_at` se
    nunca usada) — critério mais simples e defensável possível, já que a
    especificação (seção 11) lista "relevância" e "pouco uso" como
    critérios de limpeza sem detalhar uma fórmula.

    Quanto mais usos e mais recente o último uso, maior a pontuação; nunca
    negativa. Decidir o que fazer com essa pontuação (o que remover, em que
    limiar) é política de retenção, TASK-049, não implementado aqui."""
    reference = memory.last_used_at or memory.created_at
    age_days = max((now - reference).total_seconds() / 86400, 0)
    return memory.use_count / (1 + age_days)
