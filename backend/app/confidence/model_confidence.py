"""Confiança do modelo: LOW/MEDIUM/HIGH (TASK-031).

O enum `Confidence` já existe em `app.llm.protocol` (TASK-016), como
vocabulário compartilhado do protocolo JSON — reaproveitado aqui, não
duplicado (seção 13.1 da especificação mestre). Esta TASK acrescenta o que
faltava para "confiança do modelo" ser um conceito utilizável: uma ordem
explícita entre os três níveis e a leitura da confiança que o modelo
declarou na etapa final de uma execução.

O cálculo da confiança *final* — combinando confiança do modelo, evidências,
reputação de fontes e contradições (seção 13.3) — é a Confidence Engine
(TASK-033), não implementada aqui. Guardrails que agem sobre a confiança
(bloquear conclusão em `LOW`, revalidar informação volátil, tratar
ambiguidade) são TASK-034/TASK-035/TASK-036.
"""

from __future__ import annotations

from app.llm.protocol import Action, Confidence
from app.orchestrator.execution import Execution

CONFIDENCE_ORDER: dict[Confidence, int] = {
    Confidence.LOW: 0,
    Confidence.MEDIUM: 1,
    Confidence.HIGH: 2,
}
"""Ordem entre os níveis de confiança (seção 13.1): LOW < MEDIUM < HIGH."""


def is_at_least(confidence: Confidence, minimum: Confidence) -> bool:
    """`True` se `confidence` for igual ou mais alta que `minimum`, na ordem
    `LOW < MEDIUM < HIGH`."""
    return CONFIDENCE_ORDER[confidence] >= CONFIDENCE_ORDER[minimum]


class NoRespondStepError(ValueError):
    """Levantado ao pedir a confiança do modelo numa execução que ainda não
    tem uma etapa `RESPOND` registrada."""


def get_model_confidence(execution: Execution) -> Confidence:
    """Retorna a confiança que o modelo declarou na etapa `RESPOND` de
    `execution` — a confiança associada à resposta final, não a de etapas
    intermediárias (`USE_TOOL`).

    Levanta `NoRespondStepError` se a execução ainda não tiver uma etapa
    `RESPOND` registrada.
    """
    for step in reversed(execution.steps):
        if step.action == Action.RESPOND:
            return step.confidence
    raise NoRespondStepError(
        f"execução {execution.execution_id} não tem etapa RESPOND ainda"
    )
