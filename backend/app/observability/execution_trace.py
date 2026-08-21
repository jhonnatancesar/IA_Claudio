"""Execution Trace (TASK-078).

Seções 35/44 da especificação mestre (`docs/OBSERVABILITY.md`, "Execution
Trace"): "Cada execução tem um Execution Trace com: execution_id, origem,
usuário/aplicação, horário, duração, intenção, plano, etapas,
ferramentas, erros, códigos, consumo, número de passos, resultado, versão
do prompt e versão das regras do orquestrador."

Esta TASK cria só a estrutura — dataclass com todos os campos acima, mais
métodos para registrá-los ao longo de uma execução, no mesmo espírito do
modelo de `Execution` (TASK-020): sem estar conectada ao
`ExecutionOrchestrator` de verdade ainda (isso é TASK-079, "registrar
ferramentas/passos/tempos") e sem persistência no PostgreSQL (nenhuma
TASK do bloco "Observabilidade inicial", TASK-078 a TASK-083, pede isso
explicitamente — o painel read-only, TASK-081/082/083, pode vir a
precisar, mas não é desta TASK).

Mapeamento de campos da especificação para esta implementação, com as
simplificações feitas (documentadas para não parecerem esquecidas):

- `execution_id`/`origem`("origin")/`resultado`("result") — mesmo
  sentido de `Execution` (TASK-020): `origin` é quem originou a
  execução (ex.: nome da aplicação), exatamente como
  `Execution.origin` já é usado (`Execution.new(origin=application.name)`,
  TASK-069).
- `usuário/aplicação` — campo `requester`, a identidade específica de
  quem pediu a execução (pode coincidir com `origin` ou detalhar mais,
  dependendo de quem monta o trace — não decidido aqui).
- `horário`/`duração` — `started_at`/`finished_at` armazenados;
  `duration_seconds` é uma propriedade derivada (`finished_at -
  started_at`), não um campo guardado duas vezes.
- `intenção` — campo `objective` (o objetivo da execução, hoje só
  passado como parâmetro solto para `run_step`/`run_until_response`,
  nunca guardado dentro de `Execution` em si).
- `plano`/`etapas` — um único campo, `steps` (lista de `ModelStep`,
  `app.llm.protocol`, mesmo tipo de `Execution.steps`): o orquestrador
  desta V1 não mantém um objeto de "plano" separado da sequência de
  etapas decidida reativamente (`docs/ARCHITECTURE.md` — replanejar é
  descartar e gerar etapas de novo, não um objeto de plano à parte), então
  "plano" e "etapas" são a mesma informação aqui.
- `ferramentas`/`número de passos` — propriedades derivadas de `steps`
  (`tools_used`/`step_count`), não campos guardados duas vezes — mesmo
  princípio de `Execution.step_count` (TASK-020).
- `erros`/`códigos` — listas (`errors`/`error_codes`), porque a
  especificação usa plural; hoje, no comportamento real do orquestrador
  (falha para tudo, sem retry, TASK-070/QUEUE.md), no máximo um erro
  acontece por execução, mas o campo já nasce pronto para mais de um
  sem precisar redesenho depois.
- `consumo` — campo `usage`, guardado como `dict` genérico por ora;
  ligar isso a `UsageRecord` (TASK-073, que exige ida ao banco) não é
  desta TASK.
- `versão do prompt` — reaproveita `PROMPT_VERSION`
  (`app.llm.prompt`, TASK-018), não duplica o valor.
- `versão das regras do orquestrador` — campo `orchestrator_rules_version`
  existe, mas fica `None` por padrão: não há hoje nenhum esquema de
  versionamento para "as regras do orquestrador" no código (lacuna
  conhecida, registrada aqui no mesmo espírito da lacuna de retenção de
  logs já anotada em `docs/OBSERVABILITY.md`) — inventar esse esquema
  não é desta TASK.

Esta TASK (TASK-079) conecta o trace ao `ExecutionOrchestrator` de
verdade (`app.orchestrator.orchestrator`, parâmetro `trace` opcional em
`run_step`/`run_until_response`, mesmo padrão de `cancellation_token`,
TASK-030) e acrescenta o que faltava para "tempos" ter granularidade
real: `step_durations` (tempo de cada chamada ao modelo, alinhado por
índice com `steps` — `step_durations[i]` é a duração da etapa
`steps[i]`) e `tool_durations` (tempo de cada execução de ferramenta,
alinhado por índice com `tools_used` — só etapas `USE_TOOL` geram
entrada aqui, já que só elas chamam uma ferramenta de verdade).
Registro de erros (`record_error`, já existente desde a TASK-078) **não**
foi conectado ao orquestrador aqui — o título desta TASK é
especificamente "ferramentas/passos/tempos", não erros; a conexão fica
disponível para quando for pedida.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.llm.prompt import PROMPT_VERSION
from app.llm.protocol import ModelStep


@dataclass
class ExecutionTrace:
    """Registro observável de uma execução, do início ao fim."""

    execution_id: str
    origin: str
    requester: str
    objective: str
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None
    steps: list[ModelStep] = field(default_factory=list)
    step_durations: list[float] = field(default_factory=list)
    tool_durations: list[float] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    error_codes: list[int] = field(default_factory=list)
    usage: dict[str, Any] | None = None
    result: str | None = None
    prompt_version: str = PROMPT_VERSION
    orchestrator_rules_version: str | None = None

    def __post_init__(self) -> None:
        if not self.execution_id or not self.execution_id.strip():
            raise ValueError("execution_id não pode ser vazio")
        if not self.origin or not self.origin.strip():
            raise ValueError("origin não pode ser vazio")
        if not self.requester or not self.requester.strip():
            raise ValueError("requester não pode ser vazio")

    @classmethod
    def new(cls, execution_id: str, origin: str, requester: str, objective: str) -> "ExecutionTrace":
        """Cria um `ExecutionTrace` novo, com `started_at` marcado agora."""
        return cls(
            execution_id=execution_id,
            origin=origin,
            requester=requester,
            objective=objective,
        )

    @property
    def step_count(self) -> int:
        """"Número de passos" da especificação — derivado de `steps`,
        nunca guardado separadamente (evita os dois ficarem
        dessincronizados)."""
        return len(self.steps)

    @property
    def tools_used(self) -> list[str]:
        """"Ferramentas" da especificação — nomes das ferramentas usadas
        em `steps`, na ordem em que apareceram (repetidos se a mesma
        ferramenta for usada mais de uma vez)."""
        return [step.tool for step in self.steps if step.tool]

    @property
    def duration_seconds(self) -> float | None:
        """"Duração" da especificação — `None` enquanto a execução não
        tiver terminado (`finished_at` ainda não definido)."""
        if self.finished_at is None:
            return None
        return (self.finished_at - self.started_at).total_seconds()

    def add_step(self, step: ModelStep, duration_seconds: float | None = None) -> None:
        """Registra mais uma etapa (`ModelStep`) do ciclo do
        orquestrador, com o tempo que a chamada ao modelo levou
        (TASK-079) — `step_durations[i]` corresponde a `steps[i]`.
        `duration_seconds=None` fica de fora de `step_durations` (não
        entra um `None` na lista) — usado por chamadores que não medem
        tempo."""
        self.steps.append(step)
        if duration_seconds is not None:
            self.step_durations.append(duration_seconds)

    def record_tool_execution(self, duration_seconds: float) -> None:
        """Registra o tempo que a execução de uma ferramenta levou
        (TASK-079) — `tool_durations[i]` corresponde a `tools_used[i]`:
        chame isto, na ordem, uma vez para cada etapa `USE_TOOL` que
        chegou a executar a ferramenta de verdade."""
        self.tool_durations.append(duration_seconds)

    def record_error(self, error: str, code: int | None = None) -> None:
        """Registra um erro (mensagem, mais o código do catálogo se
        houver — `docs/ERROR_CATALOG.md`). Pode ser chamado mais de uma
        vez por execução."""
        self.errors.append(error)
        if code is not None:
            self.error_codes.append(code)

    def finish(self, result: str | None = None) -> None:
        """Marca `finished_at` agora e guarda o `result` final (pode ser
        `None` — uma execução que terminou em erro não tem resultado de
        sucesso)."""
        self.finished_at = datetime.now(timezone.utc)
        self.result = result
