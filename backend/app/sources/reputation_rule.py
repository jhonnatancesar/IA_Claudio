"""Atualização de reputação de fontes (TASK-062).

`set_source_reputation` (TASK-061) só aplica a troca *mecânica* de
reputação — não decide *quando* trocar. Esta TASK acrescenta essa
decisão: "se uma fonte confiável começar a apresentar dados errados ou
contraditórios, pode ser rebaixada para MEDIUM ou LOW"
(`docs/TRUST_GUARDRAILS.md`, seção 14/15). "Avaliada dinamicamente"
implica que a reputação também pode subir com resultados corretos
consistentes, não só descer — por isso a regra aqui é simétrica: um
resultado incorreto rebaixa um degrau (`HIGH → MEDIUM → LOW`), um
resultado correto eleva um degrau (`LOW → MEDIUM → HIGH`); a
especificação não detalha se a subida deveria existir ou por quanto,
então "um degrau por vez" é o critério mais simples e defensável (mesmo
espírito do threshold de `loop_detector.py`, TASK-029).

`update_reputation` é uma função pura sobre o enum — não sabe nada sobre
persistência. `update_source_reputation` busca a fonte, aplica a regra e
só grava se o resultado realmente mudar (evita "atualizações" que não
alteram nada). Histórico de cada mudança (quando, por quê) é TASK-063,
não implementado aqui — esta TASK só decide o próximo valor.
"""

from __future__ import annotations

from uuid import UUID

from app.sources.source_registry import (
    Source,
    SourceNotFoundError,
    SourceReputation,
    get_source,
    set_source_reputation,
)

_STEP_DOWN: dict[SourceReputation, SourceReputation] = {
    SourceReputation.HIGH: SourceReputation.MEDIUM,
    SourceReputation.MEDIUM: SourceReputation.LOW,
    SourceReputation.LOW: SourceReputation.LOW,
}

_STEP_UP: dict[SourceReputation, SourceReputation] = {
    SourceReputation.LOW: SourceReputation.MEDIUM,
    SourceReputation.MEDIUM: SourceReputation.HIGH,
    SourceReputation.HIGH: SourceReputation.HIGH,
}


def update_reputation(current: SourceReputation, was_accurate: bool) -> SourceReputation:
    """Calcula a próxima reputação a partir de `current` e do resultado de
    uma verificação: `was_accurate=False` rebaixa um degrau
    (`HIGH → MEDIUM → LOW`, permanece `LOW`); `was_accurate=True` eleva um
    degrau (`LOW → MEDIUM → HIGH`, permanece `HIGH`). Função pura, sem
    persistência."""
    return _STEP_UP[current] if was_accurate else _STEP_DOWN[current]


def update_source_reputation(source_id: UUID, was_accurate: bool) -> Source:
    """Busca a fonte `source_id`, calcula a nova reputação
    (`update_reputation`) e só grava (`set_source_reputation`, TASK-061)
    se o valor realmente mudar — evita gravações sem efeito. Levanta
    `SourceNotFoundError` se `source_id` não existir."""
    source = get_source(source_id)
    if source is None:
        raise SourceNotFoundError(f"fonte não encontrada: {source_id!r}")

    new_reputation = update_reputation(source.reputation, was_accurate)
    if new_reputation == source.reputation:
        return source

    return set_source_reputation(source_id, new_reputation)
