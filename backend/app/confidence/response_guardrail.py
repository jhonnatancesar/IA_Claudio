"""Bloqueio de resposta conclusiva quando a confiança final é LOW (TASK-034).

Seção 13.3 da especificação mestre: em `LOW`, o Claudião **não** pode
apresentar uma conclusão como fato — só entrega o que conseguiu verificar.
Esta TASK implementa exatamente essa guarda, como função isolada: recebe a
confiança final já calculada (Confidence Engine, TASK-033) e bloqueia
quando for `LOW`.

`MEDIUM` (responde, mas sinaliza incerteza) e a forma como essa guarda é
efetivamente acionada no fluxo do orquestrador antes de uma resposta real
ser entregue ao usuário/aplicação não são desta TASK — dependem de onde a
resposta final é montada, ainda não implementado.
"""

from __future__ import annotations

from app.errors.catalog import ErrorDomain, register_error
from app.errors.response import ClaudiaoError
from app.llm.protocol import Confidence

LOW_CONFIDENCE_BLOCKED = register_error(
    ErrorDomain.MODEL_ORCHESTRATOR,
    4006,
    409,
    "Confiança final LOW não permite resposta conclusiva",
)


def ensure_conclusive_response_allowed(final_confidence: Confidence) -> None:
    """Levanta `ClaudiaoError(LOW_CONFIDENCE_BLOCKED)` quando `final_confidence`
    for `LOW`. `MEDIUM` e `HIGH` passam livres — sinalizar incerteza em
    `MEDIUM` é responsabilidade de quem monta a resposta, não desta guarda.
    """
    if final_confidence == Confidence.LOW:
        raise ClaudiaoError(
            LOW_CONFIDENCE_BLOCKED,
            details={"final_confidence": final_confidence.value},
        )
