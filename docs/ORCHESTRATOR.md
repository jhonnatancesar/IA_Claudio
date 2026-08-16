# Orquestrador

Fonte: seções 6 a 10, 29 e 30 da especificação mestre.

Componentes do orquestrador, conforme o diagrama de `ARCHITECTURE.md`: Policy Engine,
Context Manager, Complexity/Resource Estimator, Planner, Confidence Engine,
Guardrails, Queue Manager, Tool Registry, Execution Trace.

O ciclo de execução, o protocolo JSON e a hierarquia de prioridade estão descritos em
`ARCHITECTURE.md` — este documento cobre o que não está lá: contexto de conversa,
janela de contexto, complexidade/limites de execução e replanejamento.

## Contexto de conversa

O `ContextManager` mantém:

- assunto principal
- entidades recentes
- objetivo atual
- últimas ações
- referências implícitas
- correções feitas pelo usuário

O Claudião deve entender referências como "esse", "ele", "o outro", "continua" e "faz
isso". Se houver ambiguidade real, **pergunta em vez de assumir**. A V1 mantém um
assunto principal por vez e limpa referências antigas quando houver mudança real de
tópico.

## Janela de contexto

- Configurável pelo painel; mudança exige reinicialização.
- Aviso preventivo, discreto, ao atingir 80% de uso.
- O sistema **não** transporta automaticamente contexto para outra conversa. Quando o
  limite é atingido, o usuário inicia outra conversa; se quiser continuidade, pode
  pedir um resumo/prompt de transferência e levar manualmente.

## Complexidade e limitação do chat

Antes de executar, o Claudião faz pré-avaliação de complexidade. O chat possui
orçamento mais restrito que aplicações.

- Tarefa simples: executa normalmente.
- Tarefa pesada: avisa que pode exceder a cota, mas continua até onde for permitido;
  prioriza automaticamente as partes mais importantes; sempre explica o que priorizou
  e o que ficou de fora.
- Aplicações não sofrem redução automática — devem ser respeitadas conforme o
  `ExecutionPolicy` enviado por elas.

## Limites de execução

- `max_steps` inicial sugerido: **10**, configurável conforme aplicação/contexto.
  **Aplicado (TASK-028)** — ver seção `ExecutionOrchestrator` abaixo.
- Detecção de loop. **Implementada (TASK-029)** — ver seção própria abaixo.
- Cancelamento externo/interno. **Implementado (TASK-030)** — ver seção própria
  abaixo.
- Erro irrecuperável.
- No chat não há timeout fixo (timeout é definido pela aplicação — ver `API.md`).

## Replanejamento

Quando é necessário replanejar, o agente pode descartar o restante do plano anterior e
gerar um plano completo novo. O novo plano volta a passar pela validação do
orquestrador (mesmas regras do plano inicial).

**Implementação (TASK-027):** `backend/app/orchestrator/replanner.py`,
`replan(orchestrator, old_execution, objective, model)`. O protocolo
(TASK-016) não tem uma "action" própria de replanejamento, e `Execution`
(TASK-020) não sabe "esvaziar" seu histórico no meio do caminho — descartar
o plano anterior aqui significa encerrar a execução atual (`fail()`, único
estado terminal disponível para isso hoje; um estado dedicado pode fazer
mais sentido quando `CANCELLED` existir, TASK-030) e criar uma execução nova
(`execution_id` novo, mesmo `origin`), cujo primeiro plano passa por
`plan_initial_step` (TASK-024) — que já inclui `validate_plan` (TASK-025)
dentro de `run_step`, garantindo "mesmas regras do plano inicial".
`CannotReplanFinishedExecutionError` se `old_execution` já estiver
`COMPLETED`/`FAILED`. O histórico da execução antiga não é apagado, só
marcado como encerrado — fica disponível para auditoria/debug.

## Modelo de `Execution` (TASK-020)

Implementado em `backend/app/orchestrator/execution.py`: `Execution`
(dataclass) representa uma execução em andamento — `execution_id`, `origin`, `status`
(`ExecutionStatus`: `PENDING`/`RUNNING`/`COMPLETED`/`FAILED`/`CANCELLED`
— os quatro primeiros no mesmo conjunto usado pela fila, `docs/QUEUE.md`;
`CANCELLED` adicionado na TASK-030), `steps` (lista de `ModelStep`,
TASK-016), `result`/`error`, `created_at`/`finished_at`.

Transições válidas: `start()` (`PENDING`→`RUNNING`), `add_step()` (só com
`RUNNING`), `complete(result)` (`RUNNING`→`COMPLETED`), `fail(error)`
(qualquer estado não-terminal→`FAILED`, inclusive direto de `PENDING`),
`cancel(reason)` (qualquer estado não-terminal→`CANCELLED`, TASK-030, mesmo
padrão de `fail()`). Qualquer transição fora dessas regras levanta
`InvalidExecutionStateError`. Sem lógica de política (TASK-022) — só o
modelo de dados e suas transições de estado; `max_steps`/detecção de
loop/cancelamento de fato são aplicados pelo `ExecutionOrchestrator`
(TASK-028/TASK-029/TASK-030).

## `execution_id` (TASK-021)

`backend/app/orchestrator/execution_id.py`: `generate_execution_id()` gera um
UUID4 novo a cada chamada (seção 25 da especificação: "Cada requisição recebe
um `execution_id` único"; "Reenvios e retries manuais sempre geram novo
`execution_id`"). `Execution.new(origin)` (fábrica em `execution.py`) cria uma
`Execution` já com esse `execution_id` gerado — usar isso em vez do construtor
direto quando não houver um `execution_id` externo definido, inclusive em
retries. O formato UUID gerado aqui é compatível com a checagem de
`validate_step` (TASK-017).

## `ExecutionPolicy` (TASK-022)

Implementado em `backend/app/policies/execution_policy.py` (não em
`orchestrator/` — o diagrama de `ARCHITECTURE.md` já reserva o Policy Engine
como componente próprio): `ExecutionPolicy` (dataclass imutável) —
`web_search_allowed`, `max_steps` (padrão `10`, seção 30),
`timeout_seconds`. `InvalidExecutionPolicyError` para valores inválidos
(`max_steps`/`timeout_seconds` não positivos).

Duas fábricas capturam as regras da especificação: `for_chat()` — sempre
`timeout_seconds=None` (seção 30: "No chat não haverá timeout fixo"),
pesquisa não pré-autorizada por padrão (seção 18.1: autorização é pedida por
vez, não declarada de antemão); `for_application(timeout_seconds=...)` —
exige `timeout_seconds` (seção 26: "O timeout é definido pela própria
aplicação"). Só o modelo — quem aplica a política de fato é o
`ExecutionOrchestrator` (TASK-023).

## `ExecutionOrchestrator` (TASK-023)

Implementado em `backend/app/orchestrator/orchestrator.py`: liga
`LocalLLMProvider` (TASK-014/015), composição de prompt (TASK-019), o
protocolo e sua validação (TASK-016/017) e `Execution` (TASK-020) num passo
real. `ExecutionOrchestrator(provider, policy, tool_executor=None)` guarda o
provider, a `ExecutionPolicy` (TASK-022) e o executor de ferramentas
(TASK-026).

`run_step(execution, objective, model)`: inicia a execução se `PENDING`;
**verifica o limite de `max_steps` da política antes de chamar o modelo**
(código `4004`, `MAX_STEPS_EXCEEDED`, TASK-028 — se `execution.step_count`
já atingiu `policy.max_steps`, marca `FAILED` e levanta `ClaudiaoError` sem
gastar uma chamada ao provider); compõe o prompt com o histórico atual
(`compose_prompt`); chama `provider.complete()`; valida a resposta
(`validate_step`); valida o plano contra a execução e a política
(`validate_plan`, TASK-025); registra a etapa em `execution`. Se a etapa for
`RESPOND`, conclui a execução usando `reason` como resultado (o protocolo
não define um campo de resposta final separado). Qualquer falha —
`LocalLLMProviderError` do runtime, `ClaudiaoError` do protocolo/plano/
`max_steps` — marca a execução como `FAILED` antes de propagar a exceção.
`run_until_response` (TASK-026) herda esse limite automaticamente, já que
chama `run_step` em loop.

**O que ainda não existia aqui** (TASKs futuras constroem em cima):
replanejamento (TASK-027), aplicação de `max_steps` (TASK-028), detecção de
loop (TASK-029), cancelamento (TASK-030).

## Planejamento inicial (TASK-024)

Implementado em `backend/app/orchestrator/planner.py`. No protocolo desta V1
(um JSON por etapa, seção 7) não existe um schema separado de "plano
multi-etapa" — o plano inicial descrito no ciclo do orquestrador (seção 6,
"modelo interpreta o objetivo" / "modelo cria plano") é a **primeira**
`ModelStep` decidida para a execução.

`plan_initial_step(orchestrator, execution, objective, model)` é uma casca
fina sobre `ExecutionOrchestrator.run_step` (TASK-023) que só pode ser
chamada antes de qualquer etapa existir na execução — levanta
`ExecutionAlreadyPlannedError` caso contrário. Dá nome e lugar próprios ao
"criar plano" do ciclo, distinto de continuar um ciclo já em andamento
(`orchestrator.run_step()` diretamente). Validação de que essa primeira
etapa é um plano aceitável é TASK-025; descartar e gerar um plano novo
(replanejar) é TASK-027.

## Validação de plano (TASK-025)

Implementado em `backend/app/orchestrator/plan_validator.py`:
`validate_plan(step, execution, policy)` — chamado dentro de
`ExecutionOrchestrator.run_step`, depois da validação sintática do protocolo
(`validate_step`, TASK-017). Duas checagens:

- `step.execution_id` precisa bater com `execution.execution_id` (código
  `4002`, `PLAN_EXECUTION_ID_MISMATCH`) — o modelo não pode "vazar" uma
  etapa para outra execução;
- se a etapa pede `WEB_SEARCH`, a `ExecutionPolicy.web_search_allowed`
  (TASK-022) precisa autorizar (código `4003`, `PLAN_TOOL_NOT_AUTHORIZED`) —
  ver `docs/TOOLS.md`, política de pesquisa.

Só essas duas regras por ora — validar se a ferramenta pedida existe de fato
é escopo de TASKs futuras (o Tool Registry ainda não existe, TASK-046 em
diante).

## Execução por etapas (TASK-026)

Fecha o ciclo da seção 6 da especificação mestre: "Executa uma etapa" →
"Resultado volta para o modelo" → "Modelo interpreta".

- `Execution.observations` (`backend/app/orchestrator/execution.py`) — lista
  paralela a `steps`, uma observação (ou `None`) por etapa.
  `set_last_observation(observation)` anexa o resultado da etapa mais
  recente; levanta `InvalidExecutionStateError` sem etapas ou se a última já
  tiver observação. `run_step` (TASK-023) agora monta o histórico do prompt
  incluindo essas observações.
- `ExecutionOrchestrator.run_until_response(execution, objective, model)`
  (`orchestrator.py`) — chama `run_step` em loop: se a etapa for `USE_TOOL`,
  executa via `tool_executor` (`ToolExecutor = Callable[[ModelStep], str]`,
  passado no construtor do orquestrador) e registra o resultado como
  observação antes da próxima chamada; para no primeiro `RESPOND`.
  `ToolExecutorNotConfiguredError` se nenhum `tool_executor` foi configurado.
  Qualquer exceção da ferramenta marca a execução como `FAILED`.

Nenhuma ferramenta real existe ainda — o `tool_executor` é fornecido por
quem chama (testes usam um fake). `max_steps` (TASK-028) e detecção de loop
(TASK-029) limitam um `tool_executor` mal comportado ou um modelo que nunca
decide `RESPOND` — ver as seções próprias abaixo.

## Detecção de loop (TASK-029)

Implementado em `backend/app/orchestrator/loop_detector.py`:
`detect_loop(execution, threshold=3)` — heurística mais simples e
defensável, já que a especificação (seção 30) só lista "detecção de loop"
como limite, sem detalhar o critério: as últimas `threshold` etapas são
consideradas um loop se tiverem a mesma assinatura (`action`/`tool`/
`parameters` idênticos). `RESPOND` entre as últimas `threshold` etapas nunca
conta como loop. `ExecutionOrchestrator` ganhou o parâmetro
`loop_repeat_threshold` (padrão `3`) e chama `detect_loop` logo depois de
`add_step`, quando a etapa não é `RESPOND`; se detectado, marca a execução
`FAILED` e levanta `ClaudiaoError` com o novo código `4005`
(`LOOP_DETECTED`, HTTP 409).

Repetir a mesma ferramenta com **parâmetros diferentes** a cada chamada não
é loop — é progresso real (ex.: buscas sucessivas com termos diferentes).
Só a repetição exata das últimas `threshold` decisões conta.

## Cancelamento (TASK-030)

Implementado em `backend/app/orchestrator/cancellation.py`:
`CancellationToken` — sinalizador de cancelamento cooperativo, sem threads/
async (a V1 é síncrona): `cancel(reason="cancelado")` marca o token;
`is_cancelled` é checado pelo orquestrador. `ExecutionCancelledError` é a
exceção levantada (não é `ClaudiaoError` — cancelamento é uma parada
deliberada, não uma falha de domínio; o erro JSON específico de timeout de
aplicação continua sendo TASK-071, não implementado aqui).

`Execution` ganhou o estado `CANCELLED` (previsto desde a TASK-020) e o
método `cancel(reason)` — mesmo padrão de `fail()`, qualquer estado
não-terminal pode ser cancelado. `ExecutionOrchestrator.run_step` e
`run_until_response` aceitam um `cancellation_token` opcional; se já
cancelado ao entrar em `run_step`, cancela `execution` e levanta
`ExecutionCancelledError` **antes** de checar `max_steps` ou chamar o
modelo — nenhuma chamada desperdiçada ao provider. `plan_initial_step`
(TASK-024) e `replan` (TASK-027) repassam o token adiante.

Cobre tanto cancelamento **externo** (quem chama guarda o token e cancela
de fora, ex.: usuário desiste, timeout da aplicação) quanto **interno** (o
próprio código do orquestrador, ou um `tool_executor`, pode chamar
`token.cancel(...)` antes de retornar — o mesmo mecanismo serve aos dois
casos). `CANCELLED`, já sendo um estado terminal, também bloqueia
replanejamento (`CannotReplanFinishedExecutionError`), consistente com
`COMPLETED`/`FAILED`.
