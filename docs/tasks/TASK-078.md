# TASK-078 — Criar Execution Trace

Status: **Concluída em 2026-08-21**

## Objetivo

Criar Execution Trace, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Observabilidade inicial") e `docs/OBSERVABILITY.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Observabilidade inicial" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/OBSERVABILITY.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-077 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/OBSERVABILITY.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários do Execution Trace/métricas e, quando aplicável, teste manual do painel read-only, conforme docs/TESTING.md.

## Documentação afetada

`docs/OBSERVABILITY.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-21. Novo `backend/app/observability/execution_trace.py`
— `ExecutionTrace` (dataclass, mesmo espírito do modelo de `Execution`,
TASK-020): todos os campos da especificação (seção 35/44) presentes,
como campos armazenados (`execution_id`/`origin`/`requester`/
`objective`/`started_at`/`finished_at`/`steps`/`errors`/`error_codes`/
`usage`/`result`/`prompt_version`/`orchestrator_rules_version`) ou
propriedades derivadas (`step_count`/`tools_used`/`duration_seconds`,
para não guardar a mesma informação duas vezes). `add_step`/
`record_error`/`finish` registram o ciclo de vida.

Simplificações de mapeamento, documentadas no próprio módulo: "plano" e
"etapas" da especificação viraram um único campo (`steps`) — este
orquestrador não mantém um objeto de plano separado da sequência de
etapas decidida reativamente; `prompt_version` reaproveita
`PROMPT_VERSION` (`app.llm.prompt`, TASK-018) em vez de duplicar o
valor; `orchestrator_rules_version` fica `None` por padrão — não existe
hoje nenhum esquema de versionamento para "as regras do orquestrador"
(lacuna conhecida, registrada em `docs/OBSERVABILITY.md`, não inventada
aqui).

Deliberadamente **não** conectado ao `ExecutionOrchestrator` real (isso
é TASK-079, "registrar ferramentas/passos/tempos") nem persistido no
PostgreSQL (nenhuma TASK do bloco "Observabilidade inicial" pede isso
ainda) — mesmo padrão de `Execution` (TASK-020) e `QueueItem`/`FifoQueue`
(TASK-074): a estrutura nasce completa e testável isoladamente, a
wiring com o resto do sistema é TASK futura.

16 testes unitários novos em `tests/unit/test_execution_trace.py`
(criação, validação de campos vazios, `step_count`/`tools_used`
derivados — incluindo ferramentas repetidas —, `record_error` com/sem
código e chamado múltiplas vezes, `duration_seconds` antes/depois de
`finish`, ciclo completo). Suíte completa: 640/640 testes aprovados,
zero pulados (Ollama verificado rodando antes da execução).
