"""Confidence Engine do orquestrador (TASK-033).

Calcula a confiança *final* combinando a confiança declarada pelo modelo
(TASK-031) com evidências externas — seção 13.3 da especificação mestre:

"O orquestrador calcula a confiança final usando confiança do modelo,
evidências, reputação das fontes, contradições e volatilidade.
- Pode rebaixar HIGH quando a evidência for fraca.
- Pode elevar MEDIUM quando houver evidência externa HIGH e consistente."

Reputação de fontes (TASK-059 em diante) e evidências reais de pesquisa (Web
Search Tool, TASK-088 em diante) ainda não existem — este motor recebe um
resumo abstrato da qualidade da evidência disponível (`EvidenceStrength`) em
vez de calculá-lo a partir de fontes reais. Quando essas TASKs existirem,
elas produzem esse resumo para alimentar o motor aqui, sem precisar mudar a
regra em si. Contradições e volatilidade citadas na especificação não têm
representação própria ainda (contradições dependem de conhecimento
confirmado/provisório, TASK-052 em diante) — não incluídas nesta TASK.
"""

from __future__ import annotations

from enum import StrEnum

from app.confidence.model_confidence import get_model_confidence
from app.llm.protocol import Confidence
from app.orchestrator.execution import Execution


class EvidenceStrength(StrEnum):
    """Resumo abstrato da qualidade da evidência externa disponível para uma
    etapa — até existir reputação de fontes (TASK-059+) e evidências reais
    de pesquisa (TASK-088+), quem chama o motor decide esse resumo."""

    NONE = "NONE"
    WEAK = "WEAK"
    STRONG = "STRONG"


def calculate_final_confidence(
    model_confidence: Confidence, evidence: EvidenceStrength
) -> Confidence:
    """Calcula a confiança final combinando a confiança do modelo com a
    força da evidência externa (seção 13.3).

    - `HIGH` do modelo + evidência `WEAK` ou `NONE` → rebaixa para `MEDIUM`.
    - `MEDIUM` do modelo + evidência `STRONG` → eleva para `HIGH`.
    - Qualquer outra combinação (inclusive `LOW`, que nenhuma regra eleva):
      mantém a confiança do modelo.
    """
    if model_confidence == Confidence.HIGH and evidence in (
        EvidenceStrength.WEAK,
        EvidenceStrength.NONE,
    ):
        return Confidence.MEDIUM
    if model_confidence == Confidence.MEDIUM and evidence == EvidenceStrength.STRONG:
        return Confidence.HIGH
    return model_confidence


def calculate_final_confidence_for_execution(
    execution: Execution, evidence: EvidenceStrength
) -> Confidence:
    """Atalho: lê a confiança que o modelo declarou na etapa `RESPOND` de
    `execution` (`get_model_confidence`, TASK-031) e calcula a confiança
    final a partir dela. Propaga `NoRespondStepError` se a execução ainda
    não tiver uma etapa `RESPOND`."""
    model_confidence = get_model_confidence(execution)
    return calculate_final_confidence(model_confidence, evidence)
