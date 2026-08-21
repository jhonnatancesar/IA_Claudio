# TASK-083 — Mostrar erros/logs/consumo

Status: **Concluída em 2026-08-21**

## Objetivo

Mostrar erros/logs/consumo, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Observabilidade inicial") e `docs/OBSERVABILITY.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Observabilidade inicial" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/OBSERVABILITY.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-082 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/OBSERVABILITY.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários do Execution Trace/métricas e, quando aplicável, teste manual do painel read-only, conforme docs/TESTING.md.

## Documentação afetada

`docs/OBSERVABILITY.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-21. Três funções de leitura novas, cada uma
mecânica e mecanicamente global (não escopada por aplicação/execução):
`list_recent_logs(limit=50)`
(`backend/app/observability/postgres_log_handler.py`, tabela `logs`,
TASK-006); `list_failed_execution_traces(limit=50)`
(`backend/app/observability/execution_trace.py`, traces persistidos com
`result IS NULL` — o único sinal de erro com dado real hoje, já que
`ExecutionTrace.errors`/`error_codes` nunca foram populados, decisão da
TASK-079); `list_recent_usage_records(limit=50)`
(`backend/app/usage/usage_model.py`, leitura global de `usage_records`,
diferente de `list_usage_for_application`, já escopada). Nenhuma
migration nova — as três tabelas já existiam.

`backend/app/panel/routes.py` ganhou as três seções finais do painel
inicial somente leitura: "Erros", "Logs recentes", "Consumo". Mensagens
de log também são texto livre — escapadas via `html.escape`, mesmo
tratamento já dado a `objective`/`result` na TASK-082.

Lacuna conhecida registrada explicitamente (mesmo espírito de outras já
documentadas): "Logs recentes" provavelmente aparece vazio na prática,
porque nenhum módulo da aplicação (orquestrador, API, guardrails) chama
`logger.error`/`logger.warning` em nenhum ponto real do fluxo de
execução — só os próprios testes de observabilidade exercitam o
logging. A função de leitura está correta; falta alguém popular os
dados, trabalho de conexão futuro fora do escopo desta TASK.

Verificado manualmente num navegador real (mesmo processo das
TASK-081/082): as cinco seções do painel renderizam corretamente com o
banco de desenvolvimento vazio (mensagens "nenhum X registrado ainda"
em todas). Testes de integração cobrem o caso com dado real
separadamente.

**Com esta TASK, o bloco "Observabilidade inicial" (TASK-078 a
TASK-083) está completo.**

19 testes novos: 6 unitários em `tests/unit/test_panel_routes.py`
(seções de erros/logs/consumo vazias e com dado, escape de mensagem de
log), 6 de integração em `tests/integration/test_panel_integration.py`
(`GET /panel` real com falha/log/consumo persistidos), 4 em
`tests/integration/test_execution_trace_persistence_integration.py`
(`list_failed_execution_traces`), 2 em
`tests/integration/test_usage_model_integration.py`
(`list_recent_usage_records`) e 2 em
`tests/integration/test_postgres_log_handler_integration.py`
(`list_recent_logs`). Suíte completa: 707/707 testes aprovados, zero
pulados (Ollama verificado rodando antes da execução).
