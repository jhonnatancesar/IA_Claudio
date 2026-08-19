"""Bloqueio automático de fontes (TASK-065).

`docs/TRUST_GUARDRAILS.md` (seção 14/15 da especificação mestre): "o
agente pode bloquear uma fonte automaticamente após validação." A
especificação não detalha qual validação especificamente dispara o
bloqueio — o gatilho mais simples e defensável, já construído nas TASKs
anteriores, é a própria atualização de reputação (TASK-062): "se uma
fonte confiável começar a apresentar dados errados ou contraditórios,
pode ser rebaixada para MEDIUM ou LOW", e uma fonte que caiu para `LOW`
("fonte LOW só é usada em último caso e com aviso") é candidata natural a
bloqueio automático, sem exigir um sinal novo que ainda não existe no
sistema.

`auto_block_after_validation` encadeia `update_source_reputation`
(TASK-062) com `block_source` (TASK-064, `origin=AGENT`) quando a
reputação resultante for `LOW` e a fonte ainda não estiver bloqueada —
evita `SourceBlacklistStateError` ao tentar bloquear de novo uma fonte já
bloqueada. "Bloqueio automático gera alerta no painel" não é implementado
aqui — o painel ainda não existe (TASK-081 em diante).
"""

from __future__ import annotations

from uuid import UUID

from app.sources.reputation_rule import update_source_reputation
from app.sources.source_registry import BlockOrigin, Source, SourceReputation, block_source

AUTO_BLOCK_REASON = "reputação caiu para LOW após validação"


def is_eligible_for_auto_block(reputation: SourceReputation) -> bool:
    """`True` se `reputation` torna a fonte elegível para bloqueio
    automático — hoje, só `LOW`."""
    return reputation == SourceReputation.LOW


def auto_block_after_validation(source_id: UUID, was_accurate: bool) -> Source:
    """Atualiza a reputação da fonte a partir de um resultado de
    verificação (`update_source_reputation`, TASK-062) e, se a reputação
    resultante for elegível (`is_eligible_for_auto_block`) e a fonte ainda
    não estiver bloqueada, bloqueia automaticamente
    (`block_source`, `origin=AGENT`, TASK-064). Retorna a fonte no seu
    estado final."""
    source = update_source_reputation(source_id, was_accurate)

    if is_eligible_for_auto_block(source.reputation) and not source.is_blocked:
        source = block_source(source.id, BlockOrigin.AGENT, AUTO_BLOCK_REASON)

    return source
