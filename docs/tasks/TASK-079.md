# TASK-079 — Registrar ferramentas/passos/tempos

Status: **Concluída em 2026-08-21**

## Objetivo

Registrar ferramentas/passos/tempos, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Observabilidade inicial") e `docs/OBSERVABILITY.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Observabilidade inicial" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/OBSERVABILITY.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-078 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/OBSERVABILITY.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários do Execution Trace/métricas e, quando aplicável, teste manual do painel read-only, conforme docs/TESTING.md.

## Documentação afetada

`docs/OBSERVABILITY.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-21. `ExecutionTrace` (TASK-078) conectado de
verdade ao `ExecutionOrchestrator`: `run_step`/`run_until_response`
(`backend/app/orchestrator/orchestrator.py`) ganharam um parâmetro
`trace: ExecutionTrace | None = None`, mesmo padrão de
`cancellation_token` (TASK-030) — repassado também por
`plan_initial_step` (`planner.py`) e `replan` (`replanner.py`), para
manter o mesmo threading já usado para cancelamento. Cada chamada ao
modelo é cronometrada (`time.monotonic()`) e registrada via
`trace.add_step(step, duration_seconds=...)`; cada execução de
ferramenta bem-sucedida via `trace.record_tool_execution(duration_seconds)`.
`ExecutionTrace` ganhou dois campos novos para isso: `step_durations`
(alinhado por índice com `steps`) e `tool_durations` (alinhado por
índice com `tools_used`).

`POST /v1/executions` (`backend/app/api/executions.py`) agora cria um
`ExecutionTrace` a cada requisição e passa para `run_until_response` —
populado de verdade durante a execução real. `trace.finish(...)` só é
chamado nos desfechos que a thread principal pode tocar com segurança
(sucesso, falha de modelo/ferramenta) — não no caminho de timeout, pela
mesma razão que `execution.status` também não é lido ali com confiança
total (TASK-070): a thread do orquestrador pode ainda estar escrevendo.

Decisão de escopo deliberada: registro de erros no trace
(`record_error`, já existente desde a TASK-078) **não** foi conectado
aqui — o título desta TASK é especificamente "ferramentas/passos/tempos",
não erros; a conexão fica pronta para quando for pedida. O trace também
não é persistido nem devolvido na resposta HTTP — nenhuma TASK do bloco
"Observabilidade inicial" pede isso ainda.

14 testes unitários novos: `tests/unit/test_orchestrator_trace.py` (10 —
registro de etapa/tempo em `run_step`, etapa inválida não é registrada,
`tools_used`/`tool_durations` alinhados em `run_until_response`,
comportamento sem `trace`), mais 1 em `test_planner.py` e 1 em
`test_replanner.py` (forwarding de `trace`), mais 3 em
`test_execution_trace.py` (`step_durations`/`tool_durations` via
`add_step`/`record_tool_execution`). Suíte completa: 654/654 testes
aprovados, zero pulados (Ollama verificado rodando antes da execução).
