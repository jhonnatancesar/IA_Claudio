"""Detecção de loop (TASK-029).

A especificação mestre (seção 30) lista "detecção de loop" como um dos
limites de execução, sem detalhar o critério — usa-se aqui a heurística mais
simples e defensável: repetir a mesma decisão (mesma `action`/`tool`/
`parameters`) um número de vezes seguidas, sem progresso, é tratado como
loop. Complementa `max_steps` (TASK-028): sem isso, um modelo preso
repetindo a mesma etapa só pararia no limite de `max_steps`, gastando etapas
à toa; com detecção de loop, para antes, com um erro mais específico.
"""

from __future__ import annotations

import json

from app.errors.catalog import ErrorDomain, register_error
from app.errors.response import ClaudiaoError
from app.llm.protocol import Action, ModelStep
from app.orchestrator.execution import Execution

LOOP_DETECTED = register_error(
    ErrorDomain.MODEL_ORCHESTRATOR,
    4005,
    409,
    "Loop detectado: a mesma decisão foi repetida sem progresso",
)

DEFAULT_REPEAT_THRESHOLD = 3
"""Quantas vezes seguidas a mesma decisão (action/tool/parameters) precisa
se repetir para ser considerada um loop."""


def _step_signature(step: ModelStep) -> tuple[str, str, str]:
    """Assinatura usada para comparar repetição: `action`, `tool` e
    `parameters` (serializados de forma estável e determinística)."""
    return (
        step.action.value,
        step.tool or "",
        json.dumps(step.parameters, sort_keys=True, ensure_ascii=False),
    )


def detect_loop(execution: Execution, threshold: int = DEFAULT_REPEAT_THRESHOLD) -> bool:
    """`True` se as últimas `threshold` etapas de `execution` forem
    idênticas entre si (mesma `action`/`tool`/`parameters`).

    `RESPOND` nunca conta como loop — a presença de um `RESPOND` entre as
    últimas `threshold` etapas já significa que a execução concluiu ou está
    prestes a concluir, não que está presa repetindo algo.
    """
    if threshold < 2:
        raise ValueError("threshold precisa ser pelo menos 2")
    if len(execution.steps) < threshold:
        return False

    last_steps = execution.steps[-threshold:]
    if any(step.action == Action.RESPOND for step in last_steps):
        return False

    signatures = {_step_signature(step) for step in last_steps}
    return len(signatures) == 1
