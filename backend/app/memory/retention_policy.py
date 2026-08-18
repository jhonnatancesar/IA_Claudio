"""Política de retenção da memória (TASK-049).

Seção 11 da especificação mestre (`docs/MEMORY.md`, "Limpeza"): "a memória
pode ser removida automaticamente por idade, baixa relevância, pouco uso e
limite máximo. Se voltar a ser usada antes da limpeza, a vida útil é
renovada." A especificação não detalha limiares exatos — os valores padrão
abaixo são a escolha mais simples e defensável possível (mesmo espírito do
threshold de `loop_detector.py`, TASK-029), configuráveis por parâmetro.

"Pouco uso" e "baixa relevância" já têm um sinal único combinado:
`relevance_score` (TASK-048), que cresce com `use_count` e com uso
recente — por isso esta política usa um limiar sobre ela em vez de
critérios separados de uso e relevância. "Idade" é avaliada sobre
`created_at`, independente da pontuação de relevância (uma memória pode
ter poucos usos recentes mas ainda ser nova o bastante para não ser
removida).

Limite máximo de memórias por dono é TASK-050, não implementado aqui.
Auditoria da remoção (guardar que existiu, quando e por qual regra) é
TASK-051 — `apply_retention_policy` remove sem deixar rastro, TASK-051
constrói a auditoria em cima da mesma remoção.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from app.memory.memory_model import (
    Memory,
    delete_memory,
    list_memories_for_owner,
    relevance_score,
)

DEFAULT_MAX_AGE_DAYS = 180.0
"""Idade máxima (dias desde `created_at`) antes de uma memória virar
elegível para remoção por retenção."""

DEFAULT_MIN_RELEVANCE = 0.05
"""Pontuação mínima de `relevance_score` abaixo da qual a memória conta
como baixa relevância/pouco uso para fins de retenção."""


def is_eligible_for_retention_removal(
    memory: Memory,
    now: datetime,
    *,
    max_age_days: float = DEFAULT_MAX_AGE_DAYS,
    min_relevance: float = DEFAULT_MIN_RELEVANCE,
) -> bool:
    """`True` se `memory` deve ser removida pela política de retenção: já
    passou de `max_age_days` desde `created_at` **e** sua `relevance_score`
    está abaixo de `min_relevance`. As duas condições precisam valer juntas
    — uma memória nova não é removida só por ter pouco uso ainda, e uma
    memória muito usada não é removida só por ser antiga."""
    age_days = (now - memory.created_at).total_seconds() / 86400
    return age_days >= max_age_days and relevance_score(memory, now) < min_relevance


def apply_retention_policy(
    owner_type: str,
    owner_id: str,
    now: datetime,
    *,
    max_age_days: float = DEFAULT_MAX_AGE_DAYS,
    min_relevance: float = DEFAULT_MIN_RELEVANCE,
) -> list[UUID]:
    """Remove as memórias de `owner_type`/`owner_id` elegíveis pela
    política de retenção (`is_eligible_for_retention_removal`). Retorna os
    `id`s removidos, em nenhuma ordem garantida."""
    memories = list_memories_for_owner(owner_type, owner_id)
    to_remove = [
        memory
        for memory in memories
        if is_eligible_for_retention_removal(
            memory, now, max_age_days=max_age_days, min_relevance=min_relevance
        )
    ]
    for memory in to_remove:
        delete_memory(memory.id)
    return [memory.id for memory in to_remove]
