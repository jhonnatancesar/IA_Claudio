"""Tratamento de ambiguidade (TASK-036).

`docs/ORCHESTRATOR.md` (seção 9 da especificação mestre): "Se houver
ambiguidade real, pergunta em vez de assumir." `docs/TRUST_GUARDRAILS.md`:
"Ambiguidade real gera pergunta ao usuário/aplicação em vez de suposição."
O texto da especificação não detalha um critério de detecção de ambiguidade
nem um formato próprio de "pergunta" no protocolo (`ModelStep`, TASK-016,
só tem `USE_TOOL`/`RESPOND` — uma pergunta ao usuário é um `RESPOND` cujo
`reason` é a pergunta, não uma `action` nova) — por isso esta guarda, como
`response_guardrail.py` (TASK-034) e `revalidation_guardrail.py`
(TASK-035), recebe a avaliação de ambiguidade já feita por quem chama, em
vez de tentar detectá-la aqui.

Onde a ambiguidade é de fato avaliada (interpretação do objetivo/contexto de
conversa, `ContextManager`) e onde esta guarda é acionada no fluxo real do
orquestrador não são desta TASK.
"""

from __future__ import annotations

from app.errors.catalog import ErrorDomain, register_error
from app.errors.response import ClaudiaoError

UNRESOLVED_AMBIGUITY = register_error(
    ErrorDomain.MODEL_ORCHESTRATOR,
    4008,
    409,
    "Ambiguidade real não pode ser resolvida por suposição",
)


def ensure_ambiguity_resolved_before_response(
    is_ambiguous: bool, clarification_requested: bool
) -> None:
    """Levanta `ClaudiaoError(UNRESOLVED_AMBIGUITY)` quando `is_ambiguous` for
    `True` e `clarification_requested` for `False` — uma resposta conclusiva
    não pode presumir a interpretação certa de um objetivo real e ambíguo.

    Quando `clarification_requested` for `True`, a resposta é a própria
    pergunta ao usuário/aplicação (um `RESPOND` cujo `reason` pergunta, não
    conclui) — permitida mesmo com `is_ambiguous=True`.
    """
    if is_ambiguous and not clarification_requested:
        raise ClaudiaoError(UNRESOLVED_AMBIGUITY)
