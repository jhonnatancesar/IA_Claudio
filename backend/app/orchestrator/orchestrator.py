"""`ExecutionOrchestrator` (TASK-023), com validação de plano (TASK-025),
execução por etapas (TASK-026), aplicação de `max_steps` (TASK-028),
detecção de loop (TASK-029), cancelamento (TASK-030) e registro em
Execution Trace (TASK-079).

Liga as peças já construídas — `LocalLLMProvider` (TASK-014/015), composição
de prompt (TASK-019), protocolo e sua validação sintática (TASK-016/017), a
validação de plano do orquestrador (TASK-025) e o modelo `Execution`
(TASK-020) — no ciclo descrito em docs/ARCHITECTURE.md (seção
"Orquestrador"): compõe o prompt, chama o modelo, valida a resposta, executa
a ferramenta pedida e devolve o resultado ao modelo, repetindo até haver uma
resposta final, um loop ser detectado, o limite de `max_steps`
(`ExecutionPolicy`, TASK-022) ser atingido, ou a execução ser cancelada.

Replanejamento é `app.orchestrator.replanner` (TASK-027, módulo separado).

`trace: ExecutionTrace | None` (TASK-079) é um parâmetro opcional a mais em
`run_step`/`run_until_response`, mesmo padrão de `cancellation_token`
(TASK-030) — quando fornecido, cada etapa e cada execução de ferramenta são
registradas nele com o tempo que levaram (`ExecutionTrace.add_step`/
`record_tool_execution`, `app.observability.execution_trace`). `None` por
padrão: nada muda para quem já chamava sem `trace` (todos os testes/
chamadores anteriores à TASK-079).
"""

from __future__ import annotations

import time
from typing import Callable

from app.errors.catalog import ErrorDomain, register_error
from app.errors.response import ClaudiaoError
from app.llm.prompt_composer import StepRecord, compose_prompt
from app.llm.protocol import Action, ModelStep
from app.llm.protocol_validator import validate_step
from app.llm.provider import CompletionRequest, LocalLLMProvider, LocalLLMProviderError
from app.observability.execution_trace import ExecutionTrace
from app.orchestrator.cancellation import CancellationToken, ExecutionCancelledError
from app.orchestrator.execution import Execution, ExecutionStatus
from app.orchestrator.loop_detector import DEFAULT_REPEAT_THRESHOLD, LOOP_DETECTED, detect_loop
from app.orchestrator.plan_validator import validate_plan
from app.policies.execution_policy import ExecutionPolicy

MAX_STEPS_EXCEEDED = register_error(
    ErrorDomain.MODEL_ORCHESTRATOR,
    4004,
    429,
    "Número máximo de etapas (max_steps) da execução foi atingido",
)

ToolExecutor = Callable[[ModelStep], str]
"""Função que executa a ferramenta pedida por uma etapa `USE_TOOL` e retorna
o resultado como texto (observação). Nenhuma ferramenta real existe ainda no
projeto (Tool Registry é TASK-046 em diante) — quem chama fornece a própria,
inclusive nos testes."""


class ToolExecutorNotConfiguredError(RuntimeError):
    """Levantado ao tentar executar uma etapa `USE_TOOL` sem um
    `tool_executor` configurado no `ExecutionOrchestrator`."""


class ExecutionOrchestrator:
    """Orquestra uma `Execution`, usando um `LocalLLMProvider`, uma
    `ExecutionPolicy` e, opcionalmente, um `ToolExecutor` já decididos."""

    def __init__(
        self,
        provider: LocalLLMProvider,
        policy: ExecutionPolicy,
        tool_executor: ToolExecutor | None = None,
        loop_repeat_threshold: int = DEFAULT_REPEAT_THRESHOLD,
    ) -> None:
        self.provider = provider
        self.policy = policy
        self.tool_executor = tool_executor
        self.loop_repeat_threshold = loop_repeat_threshold

    def run_step(
        self,
        execution: Execution,
        objective: str,
        model: str,
        cancellation_token: CancellationToken | None = None,
        trace: ExecutionTrace | None = None,
    ) -> ModelStep:
        """Executa um passo real do ciclo do orquestrador.

        Inicia a execução se ainda estiver `PENDING`; se `cancellation_token`
        já estiver cancelado, cancela `execution` e levanta
        `ExecutionCancelledError` antes de qualquer outra checagem (TASK-030
        — cancelamento externo/interno, verificado a cada etapa); compõe o
        prompt com o histórico atual, incluindo observações de etapas
        anteriores (`app.llm.prompt_composer`); chama o modelo; valida a
        resposta contra o protocolo (`app.llm.protocol_validator`); valida o
        plano contra a execução e a política (`app.orchestrator.plan_validator`,
        TASK-025); registra a etapa em `execution`. Se a etapa for `RESPOND`,
        conclui a execução usando `reason` como resultado (o protocolo,
        TASK-016, não define um campo de resposta final separado). Se
        `trace` for fornecido (TASK-079), a etapa também é registrada nele
        junto com o tempo que a chamada ao modelo levou
        (`ExecutionTrace.add_step`) — só quando a etapa é aceita de fato
        (depois de `validate_step`/`validate_plan` passarem), não quando o
        modelo responde algo inválido.

        Qualquer falha — do runtime (`LocalLLMProviderError`), do
        protocolo/plano (`ClaudiaoError`), o limite de `max_steps` da
        política sendo atingido (TASK-028) ou um loop sendo detectado
        (TASK-029) — marca `execution` como `FAILED` antes de propagar a
        exceção original (todas via `ClaudiaoError`, exceto a do runtime).
        Cancelamento é distinto: marca `execution` como `CANCELLED`, não
        `FAILED`.
        """
        if execution.status == ExecutionStatus.PENDING:
            execution.start()

        if cancellation_token is not None and cancellation_token.is_cancelled:
            reason = cancellation_token.reason or "execução cancelada"
            execution.cancel(reason)
            raise ExecutionCancelledError(reason)

        if execution.step_count >= self.policy.max_steps:
            error = ClaudiaoError(
                MAX_STEPS_EXCEEDED, details={"max_steps": self.policy.max_steps}
            )
            execution.fail(str(error))
            raise error

        history = [
            StepRecord(step=step, observation=observation)
            for step, observation in zip(execution.steps, execution.observations)
        ]
        prompt = compose_prompt(execution.execution_id, objective, history)
        request = CompletionRequest(prompt=prompt, model=model)

        call_started_at = time.monotonic()
        try:
            response = self.provider.complete(request)
        except LocalLLMProviderError as exc:
            execution.fail(str(exc))
            raise
        call_duration_seconds = time.monotonic() - call_started_at

        try:
            step = validate_step(response.text)
            validate_plan(step, execution, self.policy)
        except ClaudiaoError as exc:
            execution.fail(str(exc))
            raise

        execution.add_step(step)
        if trace is not None:
            trace.add_step(step, duration_seconds=call_duration_seconds)

        if step.action == Action.RESPOND:
            execution.complete(step.reason)
        elif detect_loop(execution, threshold=self.loop_repeat_threshold):
            error = ClaudiaoError(
                LOOP_DETECTED,
                details={"tool": step.tool, "repeated": self.loop_repeat_threshold},
            )
            execution.fail(str(error))
            raise error

        return step

    def run_until_response(
        self,
        execution: Execution,
        objective: str,
        model: str,
        cancellation_token: CancellationToken | None = None,
        trace: ExecutionTrace | None = None,
    ) -> ModelStep:
        """Executa etapas em sequência (seção 6 da especificação mestre:
        "Executa uma etapa" → "Resultado volta para o modelo" → "Modelo
        interpreta") até o modelo decidir `RESPOND`, o limite de `max_steps`
        da política ser atingido (TASK-028), um loop ser detectado
        (TASK-029), a execução ser cancelada (TASK-030) ou uma falha ocorrer.

        A cada etapa `USE_TOOL`, executa a ferramenta via `tool_executor` e
        registra o resultado como observação da etapa
        (`Execution.set_last_observation`), disponível para o modelo na
        próxima chamada. Levanta `ToolExecutorNotConfiguredError` se nenhum
        `tool_executor` foi configurado; qualquer exceção da execução da
        ferramenta marca `execution` como `FAILED` antes de propagar.
        `max_steps`, detecção de loop e cancelamento são verificados dentro
        de `run_step`, então se aplicam tanto ao chamar `run_step`
        diretamente quanto por aqui — `cancellation_token` é checado no
        início de cada etapa, então cancelar entre uma chamada de ferramenta
        e a próxima etapa interrompe o ciclo antes da próxima chamada ao
        modelo. `trace` (TASK-079) é repassado a `run_step` a cada etapa; o
        tempo de cada execução de ferramenta bem-sucedida também é
        registrado nele (`ExecutionTrace.record_tool_execution`).
        """
        while True:
            step = self.run_step(execution, objective, model, cancellation_token, trace)
            if step.action == Action.RESPOND:
                return step

            tool_started_at = time.monotonic()
            try:
                observation = self._execute_tool(step)
            except Exception as exc:
                execution.fail(str(exc))
                raise
            if trace is not None:
                trace.record_tool_execution(time.monotonic() - tool_started_at)
            execution.set_last_observation(observation)

    def _execute_tool(self, step: ModelStep) -> str:
        if self.tool_executor is None:
            raise ToolExecutorNotConfiguredError(
                f"nenhum tool_executor configurado para executar {step.tool!r}"
            )
        return self.tool_executor(step)
