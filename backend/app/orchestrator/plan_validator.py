"""Validação de plano pelo orquestrador (TASK-025).

Depois que o modelo decide uma etapa e ela passa pela validação sintática do
protocolo (`validate_step`, TASK-017), o orquestrador ainda valida essa
etapa contra o que só ele sabe: a execução em andamento e a política vigente
(seção 6 da especificação mestre — "Orquestrador valida o plano").

Duas checagens nesta TASK:
- o `execution_id` da etapa precisa ser o mesmo da execução (o modelo não
  pode "vazar" uma etapa para outra execução);
- se a etapa pede uma ferramenta de pesquisa (`WEB_SEARCH`), a
  `ExecutionPolicy` (TASK-022) precisa autorizar isso (`docs/TOOLS.md` —
  política de pesquisa).

Validar se a ferramenta pedida existe de fato é escopo de TASKs futuras — o
Tool Registry ainda não existe (TASK-046 em diante); aqui só valida contra o
que já está implementado.
"""

from __future__ import annotations

from app.errors.catalog import ErrorDomain, register_error
from app.errors.response import ClaudiaoError
from app.llm.protocol import Action, ModelStep
from app.orchestrator.execution import Execution
from app.policies.execution_policy import ExecutionPolicy

PLAN_EXECUTION_ID_MISMATCH = register_error(
    ErrorDomain.MODEL_ORCHESTRATOR,
    4002,
    502,
    "execution_id da etapa não corresponde à execução em andamento",
)
PLAN_TOOL_NOT_AUTHORIZED = register_error(
    ErrorDomain.MODEL_ORCHESTRATOR,
    4003,
    403,
    "Ferramenta solicitada não autorizada pela política de execução",
)

_SEARCH_TOOLS = frozenset({"WEB_SEARCH"})


def validate_plan(step: ModelStep, execution: Execution, policy: ExecutionPolicy) -> None:
    """Valida `step` contra a execução e a política.

    Levanta `ClaudiaoError` se alguma regra do orquestrador for violada; não
    levanta nada (retorna `None`) se o plano for aceitável.
    """
    if step.execution_id != execution.execution_id:
        raise ClaudiaoError(
            PLAN_EXECUTION_ID_MISMATCH,
            details={"expected": execution.execution_id, "got": step.execution_id},
        )

    if step.action == Action.USE_TOOL and step.tool in _SEARCH_TOOLS:
        if not policy.web_search_allowed:
            raise ClaudiaoError(
                PLAN_TOOL_NOT_AUTHORIZED,
                details={"tool": step.tool},
            )
