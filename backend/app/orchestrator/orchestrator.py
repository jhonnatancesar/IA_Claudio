"""`ExecutionOrchestrator` (TASK-023), com validação de plano (TASK-025),
execução por etapas (TASK-026) e aplicação de `max_steps` (TASK-028).

Liga as peças já construídas — `LocalLLMProvider` (TASK-014/015), composição
de prompt (TASK-019), protocolo e sua validação sintática (TASK-016/017), a
validação de plano do orquestrador (TASK-025) e o modelo `Execution`
(TASK-020) — no ciclo descrito em docs/ARCHITECTURE.md (seção
"Orquestrador"): compõe o prompt, chama o modelo, valida a resposta, executa
a ferramenta pedida e devolve o resultado ao modelo, repetindo até haver uma
resposta final ou o limite de `max_steps` (`ExecutionPolicy`, TASK-022) ser
atingido.

**Não** é o ciclo completo do orquestrador ainda: replanejamento é
`app.orchestrator.replanner` (TASK-027, módulo separado); detecção de loop
(TASK-029) e cancelamento (TASK-030) são TASKs futuras. Sem detecção de
loop, um `tool_executor` que sempre "resolve" sem levar a uma resposta ainda
pode consumir todas as etapas permitidas até `max_steps` barrar — TASK-029
detecta padrões repetitivos antes disso.
"""

from __future__ import annotations

from typing import Callable

from app.errors.catalog import ErrorDomain, register_error
from app.errors.response import ClaudiaoError
from app.llm.prompt_composer import StepRecord, compose_prompt
from app.llm.protocol import Action, ModelStep
from app.llm.protocol_validator import validate_step
from app.llm.provider import CompletionRequest, LocalLLMProvider, LocalLLMProviderError
from app.orchestrator.execution import Execution, ExecutionStatus
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
    ) -> None:
        self.provider = provider
        self.policy = policy
        self.tool_executor = tool_executor

    def run_step(self, execution: Execution, objective: str, model: str) -> ModelStep:
        """Executa um passo real do ciclo do orquestrador.

        Inicia a execução se ainda estiver `PENDING`; compõe o prompt com o
        histórico atual, incluindo observações de etapas anteriores
        (`app.llm.prompt_composer`); chama o modelo; valida a resposta contra
        o protocolo (`app.llm.protocol_validator`); valida o plano contra a
        execução e a política (`app.orchestrator.plan_validator`, TASK-025);
        registra a etapa em `execution`. Se a etapa for `RESPOND`, conclui a
        execução usando `reason` como resultado (o protocolo, TASK-016, não
        define um campo de resposta final separado).

        Qualquer falha — do runtime (`LocalLLMProviderError`), do
        protocolo/plano (`ClaudiaoError`) ou o limite de `max_steps` da
        política sendo atingido (também `ClaudiaoError`, TASK-028) — marca
        `execution` como `FAILED` antes de propagar a exceção original.
        """
        if execution.status == ExecutionStatus.PENDING:
            execution.start()

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

        try:
            response = self.provider.complete(request)
        except LocalLLMProviderError as exc:
            execution.fail(str(exc))
            raise

        try:
            step = validate_step(response.text)
            validate_plan(step, execution, self.policy)
        except ClaudiaoError as exc:
            execution.fail(str(exc))
            raise

        execution.add_step(step)

        if step.action == Action.RESPOND:
            execution.complete(step.reason)

        return step

    def run_until_response(
        self, execution: Execution, objective: str, model: str
    ) -> ModelStep:
        """Executa etapas em sequência (seção 6 da especificação mestre:
        "Executa uma etapa" → "Resultado volta para o modelo" → "Modelo
        interpreta") até o modelo decidir `RESPOND`, o limite de `max_steps`
        da política ser atingido (TASK-028) ou uma falha ocorrer.

        A cada etapa `USE_TOOL`, executa a ferramenta via `tool_executor` e
        registra o resultado como observação da etapa
        (`Execution.set_last_observation`), disponível para o modelo na
        próxima chamada. Levanta `ToolExecutorNotConfiguredError` se nenhum
        `tool_executor` foi configurado; qualquer exceção da execução da
        ferramenta marca `execution` como `FAILED` antes de propagar. O
        limite de `max_steps` é verificado dentro de `run_step`, então se
        aplica tanto ao chamar `run_step` diretamente quanto por aqui.
        """
        while True:
            step = self.run_step(execution, objective, model)
            if step.action == Action.RESPOND:
                return step

            try:
                observation = self._execute_tool(step)
            except Exception as exc:
                execution.fail(str(exc))
                raise
            execution.set_last_observation(observation)

    def _execute_tool(self, step: ModelStep) -> str:
        if self.tool_executor is None:
            raise ToolExecutorNotConfiguredError(
                f"nenhum tool_executor configurado para executar {step.tool!r}"
            )
        return self.tool_executor(step)
