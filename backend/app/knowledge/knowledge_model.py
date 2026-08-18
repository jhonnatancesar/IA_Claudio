"""Modelo RAW/PROVISIONAL/CONFIRMED de conhecimento (TASK-052), com
versionamento (TASK-054).

Seção 12 da especificação mestre (`docs/KNOWLEDGE.md`): conhecimento é
**separado da memória** (`app.memory`, TASK-044+) e **nunca é apagado
automaticamente** — por isso este módulo não tem uma função de remoção,
diferente de `app.memory.memory_model`. Ciclo de maturidade: "fluxo
desejado: NÃO SEI → PESQUISO → VALIDO → CONFIRMO → AVALIO UTILIDADE →
SALVO", formalizado aqui como `RAW → PROVISIONAL → CONFIRMED`.

TASK-052 criou o modelo de dados e a transição *mecânica* entre
estágios — mesmo padrão de `Execution` (TASK-020): estados válidos e um
grafo de transições permitidas (um passo por vez, sempre para frente,
nunca pulando nem voltando), sem decidir *quando* uma transição deve
acontecer. A regra de negócio que decide quando promover para
`CONFIRMED` (baseada em evidências/fontes) é TASK-057, não implementada
aqui.

Esta TASK (TASK-054) acrescenta versionamento: "se um fato confirmado
mudar, o sistema mantém a versão anterior, registra a nova versão, marca
qual é a atual, preserva... motivo da mudança" — o mesmo princípio de não
reescrita silenciosa já usado em outras partes do projeto (ex.:
`docs/DECISION_LOG.md`). `create_new_version` nunca faz `UPDATE` em
`content`; sempre insere uma linha nova, ligada à anterior por
`root_id`/`previous_version_id`, e marca a anterior como não-atual — a
unicidade de "uma versão atual por `root_id`" é garantida pelo próprio
banco (índice único parcial em
`backend/app/db/migrations/0007_knowledge_versioning.sql`). Uma nova
versão sempre começa em `RAW`: conteúdo novo ainda não foi
revalidado, mesmo que a versão anterior estivesse `CONFIRMED` — refazer o
ciclo de maturidade para o conteúdo novo é a escolha mais simples e
defensável, já que a especificação não detalha se uma nova versão herda a
maturidade da anterior.

Esta TASK (TASK-055) acrescenta escopo: `GLOBAL` ou `APPLICATION:<id>`
(seção 12) — `KnowledgeScope` mais `scope_id` (obrigatório só para
`APPLICATION`, validado em Python e reforçado por `CHECK` no schema,
`backend/app/db/migrations/0008_knowledge_scope.sql`). Padrão `GLOBAL`
quando não informado. Uma nova versão (`create_new_version`) herda o
escopo da versão anterior — mudar de escopo não é o mesmo que mudar de
conteúdo, e esta TASK não implementa nenhuma função que troque o escopo
de um conhecimento existente, muito menos automaticamente: "conhecimento
específico de uma aplicação não pode ser promovido automaticamente para
global" já é satisfeito por omissão, já que nada aqui altera escopo.

Preservar fontes (TASK-056) e avaliação de utilidade pelo orquestrador
(TASK-058) não são desta TASK.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from app.db.connection import connect

_SELECT_COLUMNS = (
    "id, status, content, created_at, root_id, version, is_current, "
    "previous_version_id, change_reason, scope_type, scope_id"
)


class KnowledgeStatus(StrEnum):
    RAW = "RAW"
    PROVISIONAL = "PROVISIONAL"
    CONFIRMED = "CONFIRMED"


class KnowledgeScope(StrEnum):
    GLOBAL = "GLOBAL"
    APPLICATION = "APPLICATION"


_VALID_TRANSITIONS: dict[KnowledgeStatus, frozenset[KnowledgeStatus]] = {
    KnowledgeStatus.RAW: frozenset({KnowledgeStatus.PROVISIONAL}),
    KnowledgeStatus.PROVISIONAL: frozenset({KnowledgeStatus.CONFIRMED}),
    KnowledgeStatus.CONFIRMED: frozenset(),
}
"""Grafo de transições válidas: só para frente, um passo por vez.
`CONFIRMED` não tem saída aqui — reverter uma confirmação é versionamento
(`create_new_version`), não uma transição de status."""


class KnowledgeNotFoundError(ValueError):
    """Levantado quando um `knowledge_id` não corresponde a nenhum
    conhecimento existente."""


class InvalidKnowledgeStatusTransitionError(ValueError):
    """Levantado ao tentar uma transição de status fora do grafo
    `RAW → PROVISIONAL → CONFIRMED`."""


class KnowledgeVersionConflictError(ValueError):
    """Levantado ao tentar criar uma nova versão a partir de um
    `knowledge_id` que não é a versão atual da sua linhagem."""


class InvalidKnowledgeScopeError(ValueError):
    """Levantado quando `scope_type`/`scope_id` são inconsistentes:
    `APPLICATION` sem `scope_id`, ou `GLOBAL` com `scope_id`."""


@dataclass(frozen=True)
class Knowledge:
    id: UUID
    status: KnowledgeStatus
    content: str
    created_at: datetime
    root_id: UUID
    version: int
    is_current: bool
    previous_version_id: UUID | None
    change_reason: str | None
    scope_type: KnowledgeScope
    scope_id: str | None


def _knowledge_from_row(row: tuple[Any, ...]) -> Knowledge:
    (
        knowledge_id,
        status,
        content,
        created_at,
        root_id,
        version,
        is_current,
        previous_version_id,
        change_reason,
        scope_type,
        scope_id,
    ) = row
    return Knowledge(
        id=knowledge_id,
        status=KnowledgeStatus(status),
        content=content,
        created_at=created_at,
        root_id=root_id,
        version=version,
        is_current=is_current,
        previous_version_id=previous_version_id,
        change_reason=change_reason,
        scope_type=KnowledgeScope(scope_type),
        scope_id=scope_id,
    )


def _validate_scope(scope_type: KnowledgeScope, scope_id: str | None) -> None:
    if scope_type == KnowledgeScope.APPLICATION and not scope_id:
        raise InvalidKnowledgeScopeError(
            "scope_id é obrigatório quando scope_type é APPLICATION"
        )
    if scope_type == KnowledgeScope.GLOBAL and scope_id:
        raise InvalidKnowledgeScopeError("scope_id deve ser vazio quando scope_type é GLOBAL")


def save_knowledge(
    content: str,
    scope_type: KnowledgeScope = KnowledgeScope.GLOBAL,
    scope_id: str | None = None,
) -> Knowledge:
    """Persiste um fato novo, sempre começando em `RAW` ("NÃO SEI" — a
    primeira captura, antes de qualquer validação) e como versão `1` da
    sua própria linhagem (`root_id == id`). `scope_type` é `GLOBAL` por
    padrão; `APPLICATION` exige `scope_id` (`InvalidKnowledgeScopeError`
    caso contrário, ou se `GLOBAL` vier com `scope_id`). Levanta
    `ValueError` para `content` vazio."""
    if not content or not content.strip():
        raise ValueError("content não pode ser vazio")
    _validate_scope(scope_type, scope_id)

    new_id = uuid4()
    with connect() as conn:
        row = conn.execute(
            "INSERT INTO knowledge (id, root_id, content, scope_type, scope_id) "
            "VALUES (%s, %s, %s, %s, %s) "
            f"RETURNING {_SELECT_COLUMNS}",
            (new_id, new_id, content, scope_type.value, scope_id),
        ).fetchone()

    return _knowledge_from_row(row)


def get_knowledge(knowledge_id: UUID) -> Knowledge | None:
    """Busca uma versão específica de conhecimento pelo seu próprio `id`.
    Retorna `None` se não existir."""
    with connect() as conn:
        row = conn.execute(
            f"SELECT {_SELECT_COLUMNS} FROM knowledge WHERE id = %s",
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
            f"RETURNING {_SELECT_COLUMNS}",
            (new_status.value, knowledge_id),
        ).fetchone()

    return _knowledge_from_row(row)


def create_new_version(knowledge_id: UUID, new_content: str, reason: str) -> Knowledge:
    """Cria uma nova versão de um fato (TASK-054), sem apagar nem
    sobrescrever a anterior: insere uma linha nova (`version` seguinte,
    `is_current=True`, `previous_version_id` apontando para a versão
    anterior, `change_reason` gravado), e marca a versão anterior como
    não-atual — na mesma transação. A nova versão sempre começa em `RAW`.

    `knowledge_id` precisa ser a versão **atual** da sua linhagem —
    levanta `KnowledgeVersionConflictError` caso contrário (e
    `KnowledgeNotFoundError` se não existir), para não criar uma
    ramificação a partir de uma versão já superada. Levanta `ValueError`
    para `new_content`/`reason` vazios."""
    if not new_content or not new_content.strip():
        raise ValueError("new_content não pode ser vazio")
    if not reason or not reason.strip():
        raise ValueError("reason não pode ser vazio")

    current = get_knowledge(knowledge_id)
    if current is None:
        raise KnowledgeNotFoundError(f"conhecimento não encontrado: {knowledge_id!r}")
    if not current.is_current:
        raise KnowledgeVersionConflictError(
            f"{knowledge_id!r} não é a versão atual da sua linhagem "
            f"(use get_current_version(root_id) para encontrá-la)"
        )

    new_id = uuid4()
    with connect() as conn:
        conn.execute(
            "UPDATE knowledge SET is_current = false WHERE id = %s",
            (current.id,),
        )
        row = conn.execute(
            "INSERT INTO knowledge "
            "(id, root_id, version, is_current, previous_version_id, "
            "change_reason, content, scope_type, scope_id) "
            "VALUES (%s, %s, %s, true, %s, %s, %s, %s, %s) "
            f"RETURNING {_SELECT_COLUMNS}",
            (
                new_id,
                current.root_id,
                current.version + 1,
                current.id,
                reason,
                new_content,
                current.scope_type.value,
                current.scope_id,
            ),
        ).fetchone()

    return _knowledge_from_row(row)


def get_current_version(root_id: UUID) -> Knowledge | None:
    """Busca a versão atual de uma linhagem de conhecimento. Retorna
    `None` se `root_id` não corresponder a nenhuma linhagem."""
    with connect() as conn:
        row = conn.execute(
            f"SELECT {_SELECT_COLUMNS} FROM knowledge "
            "WHERE root_id = %s AND is_current",
            (root_id,),
        ).fetchone()

    if row is None:
        return None
    return _knowledge_from_row(row)


def list_version_history(root_id: UUID) -> list[Knowledge]:
    """Lista todas as versões de uma linhagem, da mais antiga para a mais
    recente (`version` crescente)."""
    with connect() as conn:
        rows = conn.execute(
            f"SELECT {_SELECT_COLUMNS} FROM knowledge "
            "WHERE root_id = %s ORDER BY version ASC",
            (root_id,),
        ).fetchall()

    return [_knowledge_from_row(row) for row in rows]


def list_knowledge_for_scope(
    scope_type: KnowledgeScope, scope_id: str | None = None
) -> list[Knowledge]:
    """Lista as versões *atuais* (`is_current`) de todos os conhecimentos
    de um escopo — `GLOBAL` (todo conhecimento global) ou `APPLICATION`
    com `scope_id` (só o conhecimento daquela aplicação; nunca mistura
    aplicações diferentes nem GLOBAL com APPLICATION). Mais recente
    primeiro. Levanta `InvalidKnowledgeScopeError` para combinação
    inconsistente de `scope_type`/`scope_id` (mesma validação de
    `save_knowledge`)."""
    _validate_scope(scope_type, scope_id)

    with connect() as conn:
        if scope_type == KnowledgeScope.GLOBAL:
            rows = conn.execute(
                f"SELECT {_SELECT_COLUMNS} FROM knowledge "
                "WHERE scope_type = 'GLOBAL' AND is_current "
                "ORDER BY created_at DESC",
            ).fetchall()
        else:
            rows = conn.execute(
                f"SELECT {_SELECT_COLUMNS} FROM knowledge "
                "WHERE scope_type = 'APPLICATION' AND scope_id = %s AND is_current "
                "ORDER BY created_at DESC",
                (scope_id,),
            ).fetchall()

    return [_knowledge_from_row(row) for row in rows]
