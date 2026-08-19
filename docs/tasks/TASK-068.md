# TASK-068 — Criar validação de payload

Status: **Concluída em 2026-08-19**

## Objetivo

Criar validação de payload, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Aplicações") e `docs/API.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Aplicações" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/API.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-067 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/API.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários e de integração da API para aplicações (payload válido/inválido, timeout, execution_id, resposta final), conforme docs/TESTING.md.

## Documentação afetada

`docs/API.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-19. Criado `backend/app/api/schemas.py`:
`ExecutionRequest` (Pydantic) — `objective`/`usage_type`/
`web_search_allowed`/`timeout_seconds` obrigatórios; `context`/
`max_steps` opcionais, `None` por padrão explícito, nunca inferidos.
`POST /v1/executions` (`executions.py`) passa a receber `payload:
ExecutionRequest` em vez de `dict` genérico. Novo handler em `app.py`
converte `RequestValidationError` para o formato JSON de erro padrão do
projeto, reaproveitando `MISSING_REQUIRED_FIELD` (1001)/
`INVALID_FIELD_VALUE` (1002), já existentes desde a fundação (TASK-007)
— sem criar códigos novos.

Montar a `ExecutionPolicy` de fato a partir do payload validado e
executar via `ExecutionOrchestrator` é TASK-069, não implementado aqui.

13 testes novos (10 unitários do schema, sem tocar o banco + 3 de
integração real via `TestClient`, incluindo confirmar que erro de API
key ausente vence sobre erro de payload inválido). Suíte completa:
556/556 testes aprovados.
