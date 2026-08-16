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
- Detecção de loop.
- Cancelamento externo/interno.
- Erro irrecuperável.
- No chat não há timeout fixo (timeout é definido pela aplicação — ver `API.md`).

## Replanejamento

Quando é necessário replanejar, o agente pode descartar o restante do plano anterior e
gerar um plano completo novo. O novo plano volta a passar pela validação do
orquestrador (mesmas regras do plano inicial).

## Modelo de `Execution` (TASK-020)

Implementado em `backend/app/orchestrator/execution.py`: `Execution`
(dataclass) representa uma execução em andamento — `execution_id`, `origin`, `status`
(`ExecutionStatus`: `PENDING`/`RUNNING`/`COMPLETED`/`FAILED`, mesmo conjunto
usado pela fila — `docs/QUEUE.md`), `steps` (lista de `ModelStep`, TASK-016),
`result`/`error`, `created_at`/`finished_at`.

Transições válidas: `start()` (`PENDING`→`RUNNING`), `add_step()` (só com
`RUNNING`), `complete(result)` (`RUNNING`→`COMPLETED`), `fail(error)`
(qualquer estado não-terminal→`FAILED`, inclusive direto de `PENDING`).
Qualquer transição fora dessas regras levanta `InvalidExecutionStateError`.
Sem `CANCELLED` ainda — isso é escopo da TASK-030. Sem lógica de política
(TASK-022), execução de verdade (`ExecutionOrchestrator`, TASK-023),
`max_steps` (TASK-028) ou detecção de loop (TASK-029) — só o modelo de dados
e suas transições de estado.

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
real. `ExecutionOrchestrator(provider, policy)` guarda o provider e a
`ExecutionPolicy` (TASK-022) — a política ainda **não é aplicada**, só
guardada, para as TASKs futuras de limite.

`run_step(execution, objective, model)`: inicia a execução se `PENDING`;
compõe o prompt com o histórico atual (`compose_prompt`); chama
`provider.complete()`; valida a resposta (`validate_step`); valida o plano
contra a execução e a política (`validate_plan`, TASK-025); registra a etapa
em `execution`. Se a etapa for `RESPOND`, conclui a execução usando `reason`
como resultado (o protocolo não define um campo de resposta final separado).
Qualquer falha — `LocalLLMProviderError` do runtime ou `ClaudiaoError` do
protocolo/plano — marca a execução como `FAILED` antes de propagar a exceção.

**O que ainda não existia aqui** (TASKs futuras constroem em cima): execução de
ferramentas de verdade (TASK-026 — hoje `USE_TOOL` só é registrado, nenhuma
ferramenta roda), replanejamento (TASK-027), aplicação de `max_steps`
(TASK-028), detecção de loop (TASK-029), cancelamento (TASK-030).

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
