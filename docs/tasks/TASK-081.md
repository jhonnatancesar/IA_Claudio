# TASK-081 — Criar painel web read-only

Status: **Concluída em 2026-08-21**

## Objetivo

Criar painel web read-only, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Observabilidade inicial") e `docs/OBSERVABILITY.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Observabilidade inicial" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/OBSERVABILITY.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-080 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/OBSERVABILITY.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários do Execution Trace/métricas e, quando aplicável, teste manual do painel read-only, conforme docs/TESTING.md.

## Documentação afetada

`docs/OBSERVABILITY.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-21. Novo `backend/app/panel/routes.py`: `GET
/panel`, incluído no mesmo `app` de `app.api.app` (API de aplicações e
painel humano no mesmo processo — sem decisão de separá-los). A página
HTML mínima (sem CSS/framework) mostra a fila atual via
`app.queue.queue_model.list_queue_items` (TASK-075, já tinha dado real
persistido) — `render_panel_page(items)` monta o HTML separado da rota,
testável sem FastAPI. Só `item_id`/`status`/`created_at`/`finished_at`
aparecem; `payload` nunca é exibido (pode conter dado arbitrário de quem
enfileirou).

Duas decisões de escopo documentadas: (1) **sem autenticação** — as
regras de acesso de `docs/PANEL.md` (confirmação, senha `ADMIN`, logout
por inatividade) valem para o painel administrativo completo (TASK-115+),
não para este painel inicial somente leitura; nenhuma TASK anterior
construiu sessão de usuário via navegador, então exigir login aqui seria
inventar mecanismo não pedido; (2) só a fila é mostrada — "execução
atual"/"resultados das execuções" (TASK-082) e "logs/erros/consumo"
(TASK-083) ficam para as próximas TASKs, que provavelmente vão esbarrar
numa decisão de arquitetura nova, já que `ExecutionTrace` (TASK-078/079)
não é persistido em lugar nenhum ainda.

Verificado manualmente num navegador real (`preview_start` +
`uvicorn app.api.app:app`, TestClient dispensado para essa checagem
específica): página carrega, mostra "Fila vazia." sem itens, e mostra um
item inserido de propósito (removido depois) com `item_id`/`status`/
`created_at` corretos.

8 testes novos: 5 unitários em `tests/unit/test_panel_routes.py`
(`render_panel_page` isolada) e 3 de integração em
`tests/integration/test_panel_integration.py` (`GET /panel` real via
`TestClient`, item persistido de verdade). Suíte completa: 676/676
testes aprovados, zero pulados (Ollama verificado rodando antes da
execução).
