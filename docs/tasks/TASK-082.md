# TASK-082 — Mostrar execuções no painel

Status: **Concluída em 2026-08-21**

## Objetivo

Mostrar execuções no painel, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Observabilidade inicial") e `docs/OBSERVABILITY.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Observabilidade inicial" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/OBSERVABILITY.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-081 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/OBSERVABILITY.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários do Execution Trace/métricas e, quando aplicável, teste manual do painel read-only, conforme docs/TESTING.md.

## Documentação afetada

`docs/OBSERVABILITY.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-21. Esta TASK esbarrou num ponto que a
especificação mestre não decide: `ExecutionTrace` (TASK-078/079) só
existe durante a duração de uma requisição HTTP, nunca persistido —
sem isso, o painel não teria como mostrar execuções passadas. Pedido
explicitamente ao usuário via `AskUserQuestion` (duas opções: reaproveitar
`usage_records` já persistido, sem tabela nova mas sem
objetivo/resultado/etapas; ou persistir o Execution Trace numa tabela
nova). O usuário escolheu persistir o Execution Trace — registrado como
`DEC-010` em `docs/DECISION_LOG.md`.

Migration `backend/app/db/migrations/0017_execution_traces.sql` — tabela
`execution_traces` (`execution_id` PK, `origin`, `requester`,
`objective`, `started_at`, `finished_at`, `result`, `step_count`,
`tools_used jsonb`, `prompt_version`, `created_at`). Só o **resumo** é
guardado — não `steps` completos (cada `ModelStep` com parâmetros
arbitrários) nem `step_durations`/`tool_durations` individuais, nem
`errors`/`error_codes`/`usage`/`orchestrator_rules_version` (continuam
sem fonte de dado real). `backend/app/observability/execution_trace.py`
ganhou `save_execution_trace`/`get_execution_trace`/
`list_execution_traces` e um novo modelo de leitura,
`ExecutionTraceRecord` (deliberadamente separado de `ExecutionTrace`,
para não fingir que campos nunca gravados vieram do banco).
`POST /v1/executions` chama `save_execution_trace(trace)` logo depois de
`trace.finish(...)`, nos mesmos desfechos seguros de tocar (sucesso,
falha de modelo/ferramenta — não no timeout, mesma razão já aplicada a
`execution`/`trace` nas TASK-070/079).

`backend/app/panel/routes.py` ganhou a seção "Execuções": `execution_id`/
`requester`/`objective`/status (derivado de `succeeded`)/`result`/
`duration_seconds`. `objective`/`result` são texto livre vindo da
aplicação chamadora/do modelo — escapados via `html.escape` antes de
entrar na página (diferente dos campos da fila, todos gerados pelo
próprio sistema). Verificado manualmente num navegador real (mesmo
processo da TASK-081): trace inserido de propósito aparece corretamente
formatado, removido depois.

12 testes novos: 4 unitários em `tests/unit/test_panel_routes.py`
(execuções vazias, campos, status sucesso/falha, escape de HTML), 2 de
integração em `tests/integration/test_panel_integration.py` (`GET
/panel` real mostrando um trace persistido) e 6 de integração em
`tests/integration/test_execution_trace_persistence_integration.py`
(save/get/list, atualização por `ON CONFLICT`, item desconhecido, ordem
mais recente primeiro, limite). Suíte completa: 688/688 testes
aprovados, zero pulados (Ollama verificado rodando antes da execução).
