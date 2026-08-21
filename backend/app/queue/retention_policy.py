"""Política de retenção/limpeza da fila (TASK-077).

Seção 27 da especificação mestre (`docs/QUEUE.md`, "Retenção e falhas"):
"Registros antigos são removidos conforme política de retenção." A
especificação não detalha limiares exatos — o valor padrão abaixo é a
escolha mais simples e defensável possível (mesmo espírito de outros
limiares já definidos em código sem exigir decisão de arquitetura à
parte: `DEFAULT_MAX_STEPS`, TASK-028; `DEFAULT_MAX_AGE_DAYS` da memória,
TASK-049), configurável por parâmetro.

Diferente da memória (TASK-049, que preserva conhecimento de longo
prazo e por isso usa uma janela de 180 dias), um item de fila representa
trabalho de processamento já concluído — não há razão para mantê-lo por
muito tempo depois de terminar. `DEFAULT_MAX_AGE_DAYS = 7.0` (uma
semana) é o valor escolhido aqui.

Só itens em estado **terminal** (`COMPLETED`/`FAILED`) são elegíveis —
um item `PENDING`/`RUNNING` nunca é removido por idade, mesmo que muito
antigo, porque ainda representa trabalho em aberto (removê-lo silenciaria
uma falha real de processamento, não uma limpeza de rotina). A idade é
contada a partir de `finished_at` (quando o item terminou), não de
`created_at` (quando entrou na fila) — um item que ficou muito tempo
`PENDING` antes de ser processado não deve ser punido por isso.
"""

from __future__ import annotations

from datetime import datetime

from app.queue.queue_model import QueueItem, delete_queue_item, list_queue_items

DEFAULT_MAX_AGE_DAYS = 7.0
"""Idade máxima (dias desde `finished_at`) antes de um item terminal
virar elegível para remoção por retenção."""


def is_eligible_for_retention_removal(
    item: QueueItem,
    now: datetime,
    *,
    max_age_days: float = DEFAULT_MAX_AGE_DAYS,
) -> bool:
    """`True` se `item` deve ser removido pela política de retenção:
    está num estado terminal (`COMPLETED`/`FAILED`) **e** já passou de
    `max_age_days` desde `finished_at`. Itens não-terminais nunca são
    elegíveis, independente da idade."""
    if not item.is_terminal or item.finished_at is None:
        return False
    age_days = (now - item.finished_at).total_seconds() / 86400
    return age_days >= max_age_days


def apply_retention_policy(
    now: datetime, *, max_age_days: float = DEFAULT_MAX_AGE_DAYS
) -> list[str]:
    """Remove os itens persistidos elegíveis pela política de retenção
    (`is_eligible_for_retention_removal`). Retorna os `item_id`s
    removidos, em nenhuma ordem garantida."""
    items = list_queue_items()
    to_remove = [
        item
        for item in items
        if is_eligible_for_retention_removal(item, now, max_age_days=max_age_days)
    ]
    for item in to_remove:
        delete_queue_item(item.item_id)
    return [item.item_id for item in to_remove]
