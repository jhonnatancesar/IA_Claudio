# TASK-071 — Implementar erro de timeout

Status: **Concluída em 2026-08-19**

## Objetivo

Implementar erro de timeout, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Aplicações") e `docs/API.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Aplicações" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/API.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-070 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/API.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários e de integração da API para aplicações (payload válido/inválido, timeout, execution_id, resposta final), conforme docs/TESTING.md.

## Documentação afetada

`docs/API.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-19. `APPLICATION_TIMEOUT_EXCEEDED` (código `4009`,
introduzido na TASK-070) agora carrega o formato específico exigido pela
seção 26 da especificação mestre — "registra etapa atual e ferramenta
ativa" — nos seus `details`. Extraída
`_timeout_error_details(execution, timeout_seconds)`
(`backend/app/api/executions.py`), função pura chamada pela rota no
`except FutureTimeoutError`: `current_step` é `execution.step_count + 1`
(1-indexado, a etapa em andamento no momento do timeout); `active_tool` é
o `tool` da última etapa já registrada em `execution.steps`, ou `None`
se nenhuma foi registrada ainda ou a última não usava ferramenta.

Como nenhum `tool_executor` está configurado ainda em `POST
/v1/executions` (Tool Registry é TASK-088 em diante), o caminho real do
endpoint hoje quase sempre trava na primeira chamada ao modelo — antes de
qualquer etapa ser registrada —, então `current_step: 1`/`active_tool:
null` é o resultado comum na prática agora; o valor só cresce em
utilidade quando fluxos `USE_TOOL` reais existirem. Por isso o cenário
"ferramenta ativa preenchida" é coberto por teste unitário direto de
`_timeout_error_details` (construindo o estado de `Execution` à mão),
não por um teste de integração via HTTP — não é alcançável de ponta a
ponta com o sistema atual.

3 testes unitários novos em `tests/unit/test_api_executions.py`, testando
`_timeout_error_details` isoladamente (sem etapa registrada, com uma
etapa `USE_TOOL` registrada, com múltiplas). O teste de integração de
timeout já existente (TASK-070,
`tests/integration/test_api_executions_integration.py`) ganhou
assertions extras para `current_step`/`active_tool` no cenário real
alcançável hoje (nenhuma etapa registrada). Suíte completa: 565/565
testes aprovados, zero pulados (Ollama local verificado rodando antes da
execução).
