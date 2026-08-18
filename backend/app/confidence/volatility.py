"""Volatilidade: VOLATILE/NON_VOLATILE (TASK-032).

"Informação VOLATILE deve ser revalidada sempre que for usada, mesmo se o
modelo estiver em HIGH" (docs/TRUST_GUARDRAILS.md, seção 13.2 da
especificação mestre — o texto inteiro da seção é só isso). Volatilidade é
uma propriedade da informação/conhecimento usado para responder, não do
protocolo JSON por etapa (TASK-016) — este módulo só formaliza o enum e a
regra de revalidação. Onde a volatilidade de um fato é registrada e
consultada de verdade é escopo do Knowledge Tool (TASK-052 em diante), não
implementado ainda; aplicar essa regra como guardrail de fato (bloquear/
forçar revalidação antes de responder) é TASK-035, também não implementado
aqui.
"""

from __future__ import annotations

from enum import StrEnum


class Volatility(StrEnum):
    VOLATILE = "VOLATILE"
    NON_VOLATILE = "NON_VOLATILE"


def requires_revalidation(volatility: Volatility) -> bool:
    """`True` se a informação precisa ser revalidada antes de ser usada.

    Regra da seção 13.2: informação `VOLATILE` sempre precisa — mesmo com
    confiança `HIGH` (a confiança do modelo não entra nesta decisão de
    propósito: a revalidação de `VOLATILE` independe dela). Informação
    `NON_VOLATILE` não é forçada a revalidar por este critério.
    """
    return volatility == Volatility.VOLATILE
