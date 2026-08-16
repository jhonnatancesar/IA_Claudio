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
(dataclass) representa uma execução em andamento — `execution_id` (recebido
pronto; gerar/garantir unicidade é TASK-021), `origin`, `status`
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
