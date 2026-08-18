"""Regra obrigatória para informação volátil (TASK-035).

Seção 13.2 da especificação mestre: informação `VOLATILE` deve ser
**revalidada sempre que for usada**, mesmo se o modelo estiver em `HIGH`.
`requires_revalidation()` (TASK-032) já diz *se* uma revalidação é exigida;
esta TASK acrescenta a guarda que efetivamente bloqueia o uso quando ela foi
exigida e não aconteceu.

Onde a revalidação em si é executada (reconsultar a fonte/Knowledge Tool,
TASK-052 em diante) e onde esta guarda é acionada no fluxo real do
orquestrador antes de uma resposta não são desta TASK — só a guarda
isolada, análoga a `response_guardrail.py` (TASK-034).
"""

from __future__ import annotations

from app.confidence.volatility import Volatility, requires_revalidation
from app.errors.catalog import ErrorDomain, register_error
from app.errors.response import ClaudiaoError

VOLATILE_INFORMATION_NOT_REVALIDATED = register_error(
    ErrorDomain.MODEL_ORCHESTRATOR,
    4007,
    409,
    "Informação volátil usada sem revalidação obrigatória",
)


def ensure_volatile_information_revalidated(
    volatility: Volatility, was_revalidated: bool
) -> None:
    """Levanta `ClaudiaoError(VOLATILE_INFORMATION_NOT_REVALIDATED)` quando
    `volatility` exigir revalidação (`requires_revalidation`, TASK-032) e
    `was_revalidated` for `False`.

    Informação `NON_VOLATILE`, ou `VOLATILE` já revalidada, passam livres.
    """
    if requires_revalidation(volatility) and not was_revalidated:
        raise ClaudiaoError(
            VOLATILE_INFORMATION_NOT_REVALIDATED,
            details={"volatility": volatility.value},
        )
