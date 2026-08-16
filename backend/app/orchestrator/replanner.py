"""Replanejamento completo (TASK-027).

"Quando é necessário replanejar, o agente pode descartar o restante do
plano anterior e gerar um plano completo novo. O novo plano volta a passar
pela validação do orquestrador (mesmas regras do plano inicial)"
(docs/ORCHESTRATOR.md, seção "Replanejamento").

Nesta V1 não existe uma "action" própria de replanejamento no protocolo
(TASK-016) — replanejar é um passo do orquestrador, não uma decisão que o
modelo declara num campo JSON. `Execution` (TASK-020) também não tem como
"esvaziar" seu histórico de etapas no meio do caminho, então descartar o
plano anterior aqui significa: encerrar a execução atual (marcá-la `FAILED`,
único estado terminal disponível para isso — um estado dedicado pode fazer
mais sentido quando `CANCELLED` existir, TASK-030) e criar uma execução nova
(`execution_id` novo, mesmo espírito de reenvio da seção 25), cujo primeiro
plano passa pelas mesmas regras do plano inicial: `plan_initial_step`
(TASK-024), que já inclui a validação de plano (`validate_plan`, TASK-025)
dentro de `run_step`.
"""

from __future__ import annotations

from app.llm.protocol import ModelStep
from app.orchestrator.cancellation import CancellationToken
from app.orchestrator.execution import Execution
from app.orchestrator.orchestrator import ExecutionOrchestrator
from app.orchestrator.planner import plan_initial_step

_REPLAN_DISCARD_MESSAGE = "descartada: substituída por replanejamento completo"


class CannotReplanFinishedExecutionError(RuntimeError):
    """Levantado ao tentar replanejar uma execução que já terminou
    (`COMPLETED` ou `FAILED`)."""


def replan(
    orchestrator: ExecutionOrchestrator,
    old_execution: Execution,
    objective: str,
    model: str,
    cancellation_token: CancellationToken | None = None,
) -> tuple[Execution, ModelStep]:
    """Descarta `old_execution` e gera um plano completo novo numa execução
    nova, com o mesmo `origin`.

    Levanta `CannotReplanFinishedExecutionError` se `old_execution` já
    estiver em estado terminal (incluindo `CANCELLED`, TASK-030) — não há
    plano "restante" para descartar numa execução que já acabou.
    `cancellation_token` é repassado para o plano da execução nova.
    """
    if old_execution.is_terminal:
        raise CannotReplanFinishedExecutionError(
            f"execução {old_execution.execution_id} já está em estado "
            f"terminal ({old_execution.status}) — não é possível replanejar"
        )
    old_execution.fail(_REPLAN_DISCARD_MESSAGE)

    new_execution = Execution.new(origin=old_execution.origin)
    step = plan_initial_step(orchestrator, new_execution, objective, model, cancellation_token)
    return new_execution, step
