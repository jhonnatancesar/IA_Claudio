"""`ExecutionOrchestrator` (TASK-023).

Liga as peças já construídas — `LocalLLMProvider` (TASK-014/015), composição
de prompt (TASK-019), protocolo e sua validação (TASK-016/017) e o modelo
`Execution` (TASK-020) — num único passo real do ciclo descrito em
docs/ARCHITECTURE.md (seção "Orquestrador"): compõe o prompt, chama o
modelo, valida a resposta e registra a etapa.

**Não** é o ciclo completo do orquestrador ainda: planejamento (TASK-024),
validação de plano (TASK-025), execução por etapas com ferramentas
(TASK-026), replanejamento (TASK-027), aplicação de `max_steps` (TASK-028),
detecção de loop (TASK-029) e cancelamento (TASK-030) são TASKs futuras que
constroem em cima do que existe aqui. A `ExecutionPolicy` é recebida e
guardada, mas **ainda não é aplicada** — isso também é escopo dessas TASKs
futuras (ex.: `max_steps` só é imposto na TASK-028).
"""

from __future__ import annotations

from app.errors.response import ClaudiaoError
from app.llm.prompt_composer import StepRecord, compose_prompt
from app.llm.protocol import Action, ModelStep
from app.llm.protocol_validator import validate_step
from app.llm.provider import CompletionRequest, LocalLLMProvider, LocalLLMProviderError
from app.orchestrator.execution import Execution, ExecutionStatus
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
        resposta contra o protocolo (`app.llm.protocol_validator`); registra
        a etapa em `execution`. Se a etapa for `RESPOND`, conclui a execução
        usando `reason` como resultado (o protocolo, TASK-016, não define um
        campo de resposta final separado).

        Qualquer falha — do runtime (`LocalLLMProviderError`) ou do protocolo
        (`ClaudiaoError`) — marca `execution` como `FAILED` antes de propagar
        a exceção original.
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
        except ClaudiaoError as exc:
            execution.fail(str(exc))
            raise

        execution.add_step(step)

        if step.action == Action.RESPOND:
            execution.complete(step.reason)

        return step
