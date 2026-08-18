"""Regra de promoção de conhecimento para CONFIRMED (TASK-057).

`advance_knowledge_status` (TASK-052) só aplica a transição *mecânica* de
status — não decide *quando* uma promoção é apropriada. Esta TASK
acrescenta essa decisão para `PROVISIONAL → CONFIRMED`: "fluxo desejado:
NÃO SEI → PESQUISO → VALIDO → CONFIRMO..." (`docs/KNOWLEDGE.md`, seção
12) — `CONFIRMO` exige mais do que só ter passado por `VALIDO`
(`PROVISIONAL`).

A especificação não detalha uma fórmula exata de elegibilidade — o
critério aqui é o mais simples e defensável possível (mesmo espírito do
threshold de `loop_detector.py`, TASK-029): confiança `HIGH`
(`app.llm.protocol.Confidence`, reaproveitada via TASK-056) **e** pelo
menos `MIN_EVIDENCE_COUNT_FOR_CONFIRMATION` evidência registrada
(`app.knowledge.knowledge_model.add_evidence`, TASK-056). Reputação real
de fontes (TASK-059 em diante) não entra nesse critério ainda — quando
existir, pode refinar a regra sem mudar sua forma.

Promoção `RAW → PROVISIONAL` não é desta TASK — o título e a
especificação tratam especificamente da promoção *para* `CONFIRMED`.
Avaliação de utilidade pelo orquestrador é TASK-058, um conceito
diferente (não é sobre maturidade do fato, é sobre se vale a pena usá-lo
numa resposta).
"""

from __future__ import annotations

from uuid import UUID

from app.knowledge.knowledge_model import (
    Knowledge,
    KnowledgeNotFoundError,
    KnowledgeStatus,
    advance_knowledge_status,
    get_knowledge,
    list_evidence,
)
from app.llm.protocol import Confidence

MIN_EVIDENCE_COUNT_FOR_CONFIRMATION = 1
"""Quantidade mínima de evidências registradas para um conhecimento
`PROVISIONAL` ser elegível à promoção para `CONFIRMED`."""


class KnowledgePromotionNotEligibleError(ValueError):
    """Levantado ao tentar promover um conhecimento para `CONFIRMED` sem
    atender ao critério de elegibilidade (status, confiança ou
    evidências insuficientes)."""


def is_eligible_for_confirmation(knowledge: Knowledge, evidence_count: int) -> bool:
    """`True` se `knowledge` pode ser promovido para `CONFIRMED`: precisa
    estar em `PROVISIONAL`, ter confiança `HIGH` e pelo menos
    `MIN_EVIDENCE_COUNT_FOR_CONFIRMATION` evidências registradas."""
    return (
        knowledge.status == KnowledgeStatus.PROVISIONAL
        and knowledge.confidence == Confidence.HIGH
        and evidence_count >= MIN_EVIDENCE_COUNT_FOR_CONFIRMATION
    )


def promote_to_confirmed(knowledge_id: UUID) -> Knowledge:
    """Aplica a regra de promoção: busca o conhecimento e suas evidências,
    verifica elegibilidade (`is_eligible_for_confirmation`) e, se
    elegível, avança o status para `CONFIRMED`
    (`advance_knowledge_status`). Levanta `KnowledgeNotFoundError` se
    `knowledge_id` não existir, e `KnowledgePromotionNotEligibleError` se
    não atender ao critério — nesse caso nada é alterado."""
    knowledge = get_knowledge(knowledge_id)
    if knowledge is None:
        raise KnowledgeNotFoundError(f"conhecimento não encontrado: {knowledge_id!r}")

    evidence_count = len(list_evidence(knowledge_id))
    if not is_eligible_for_confirmation(knowledge, evidence_count):
        raise KnowledgePromotionNotEligibleError(
            f"{knowledge_id!r} não é elegível para promoção a CONFIRMED "
            f"(status={knowledge.status}, confidence={knowledge.confidence}, "
            f"evidence_count={evidence_count})"
        )

    return advance_knowledge_status(knowledge_id, KnowledgeStatus.CONFIRMED)
