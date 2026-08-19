# TASK-072 — Implementar resposta JSON final

Status: **Concluída em 2026-08-19**

## Objetivo

Implementar resposta JSON final, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Aplicações") e `docs/API.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Aplicações" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/API.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-071 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/API.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários e de integração da API para aplicações (payload válido/inválido, timeout, execution_id, resposta final), conforme docs/TESTING.md.

## Documentação afetada

`docs/API.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-19. A resposta de sucesso de `POST /v1/executions`
agora segue o mesmo envelope `{"success": bool, ...}` já usado pelo erro
desde a TASK-008 — antes desta TASK a resposta de sucesso era o dict cru
(`execution_id`/`status`/`result` direto no nível superior, sem
`success`), inconsistente com `{"success": false, "error": {...}}`.
Criado `build_success_response(data)` em novo
`backend/app/api/responses.py`, espelhando `build_error_response`
(TASK-008, `app.errors.response`): monta `{"success": true, "data":
data}`. `create_execution` agora devolve `build_success_response({
"execution_id": ..., "status": ..., "result": ...})`.

`docs/ERROR_CATALOG.md` renomeou "Formato padrão de erro" para "Formato
padrão de resposta", documentando os dois formatos (erro já existia,
sucesso é novo aqui) — é a fonte de verdade do contrato, referenciada por
`docs/API.md`.

2 testes unitários novos em `tests/unit/test_api_responses.py`
(`build_success_response` isolada). Os testes de integração existentes
de `POST /v1/executions` (sucesso, `execution_id` único, timeout) foram
ajustados para ler `body["data"][...]` em vez do formato antigo sem
envelope — nenhum teste novo de integração foi necessário, já que os
cenários de sucesso já existentes cobrem o novo formato. Suíte completa:
567/567 testes aprovados, zero pulados (Ollama local verificado rodando
antes da execução).
