"""Planejamento inicial (TASK-024).

O ciclo do orquestrador (docs/ARCHITECTURE.md, seção "Orquestrador") começa
com o modelo interpretando o objetivo e criando um plano. No protocolo desta
V1 (um JSON por etapa — seção 7 da especificação mestre) não existe um schema
separado de "plano multi-etapa": o plano inicial é a primeira `ModelStep`
decidida para a execução — `USE_TOOL` (se precisar de uma ferramenta antes de
poder responder) ou `RESPOND` (se já souber a resposta). TASK-025 valida essa
primeira etapa como plano aceitável; TASK-027 permite descartar e gerar um
plano novo (replanejar).

`plan_initial_step` é uma casca fina sobre `ExecutionOrchestrator.run_step`
(TASK-023) que só pode ser chamada no início de uma execução — dá nome e
lugar próprios ao "criar plano" do ciclo, distinto de continuar um ciclo já
em andamento (isso é `orchestrator.run_step()` diretamente).
"""

from __future__ import annotations

from app.llm.protocol import ModelStep
from app.observability.execution_trace import ExecutionTrace
from app.orchestrator.cancellation import CancellationToken
from app.orchestrator.execution import Execution
from app.orchestrator.orchestrator import ExecutionOrchestrator


class ExecutionAlreadyPlannedError(RuntimeError):
    """Levantado ao tentar planejar uma execução que já tem etapas."""


def plan_initial_step(
    orchestrator: ExecutionOrchestrator,
    execution: Execution,
    objective: str,
    model: str,
    cancellation_token: CancellationToken | None = None,
    trace: ExecutionTrace | None = None,
) -> ModelStep:
    """Faz a primeira chamada ao modelo para uma execução nova: interpreta o
    objetivo e decide a primeira etapa (o plano inicial do ciclo).

    Só pode ser chamada antes de qualquer etapa existir em `execution` —
    levanta `ExecutionAlreadyPlannedError` caso contrário.
    `cancellation_token` (TASK-030) e `trace` (TASK-079) são repassados
    para `run_step`.
    """
    if execution.steps:
        raise ExecutionAlreadyPlannedError(
            "execução já tem etapas — planejamento inicial só vale no começo"
        )
    return orchestrator.run_step(execution, objective, model, cancellation_token, trace)
