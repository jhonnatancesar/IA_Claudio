"""`ExecutionOrchestrator` (TASK-023), com validação de plano (TASK-025).

Liga as peças já construídas — `LocalLLMProvider` (TASK-014/015), composição
de prompt (TASK-019), protocolo e sua validação sintática (TASK-016/017), a
validação de plano do orquestrador (TASK-025) e o modelo `Execution`
(TASK-020) — num único passo real do ciclo descrito em
docs/ARCHITECTURE.md (seção "Orquestrador"): compõe o prompt, chama o
modelo, valida a resposta e registra a etapa.

**Não** é o ciclo completo do orquestrador ainda: execução por etapas com
ferramentas (TASK-026), replanejamento (TASK-027), aplicação de `max_steps`
(TASK-028), detecção de loop (TASK-029) e cancelamento (TASK-030) são TASKs
futuras que constroem em cima do que existe aqui. A `ExecutionPolicy` é
usada pela validação de plano (autorização de pesquisa), mas `max_steps`
ainda não é imposto — isso é a TASK-028.
"""

from __future__ import annotations

from app.errors.response import ClaudiaoError
from app.llm.prompt_composer import StepRecord, compose_prompt
from app.llm.protocol import Action, ModelStep
from app.llm.protocol_validator import validate_step
from app.llm.provider import CompletionRequest, LocalLLMProvider, LocalLLMProviderError
from app.orchestrator.execution import Execution, ExecutionStatus
from app.orchestrator.plan_validator import validate_plan
from app.policies.execution_policy import ExecutionPolicy


class ExecutionOrchestrator:
    """Orquestra uma `Execution`, usando um `LocalLLMProvider` e uma
    `ExecutionPolicy` já decididos."""

    def __init__(self, provider: LocalLLMProvider, policy: ExecutionPolicy) -> None:
        self.provider = provider
        self.policy = policy

    def run_step(self, execution: Execution, objective: str, model: str) -> ModelStep:
        """Executa um passo real do ciclo do orquestrador.

        Inicia a execução se ainda estiver `PENDING`; compõe o prompt com o
        histórico atual (`app.llm.prompt_composer`); chama o modelo; valida a
        resposta contra o protocolo (`app.llm.protocol_validator`); valida o
        plano contra a execução e a política (`app.orchestrator.plan_validator`,
        TASK-025); registra a etapa em `execution`. Se a etapa for `RESPOND`,
        conclui a execução usando `reason` como resultado (o protocolo,
        TASK-016, não define um campo de resposta final separado).

        Qualquer falha — do runtime (`LocalLLMProviderError`) ou do
        protocolo/plano (`ClaudiaoError`) — marca `execution` como `FAILED`
        antes de propagar a exceção original.
        """
        if execution.status == ExecutionStatus.PENDING:
            execution.start()

        history = [StepRecord(step=step) for step in execution.steps]
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
