# TASK-067 — Criar API local do Claudião

Status: **Concluída em 2026-08-19**

## Objetivo

Criar API local do Claudião, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Aplicações") e `docs/API.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Aplicações" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/API.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-066 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/API.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários e de integração da API para aplicações (payload válido/inválido, timeout, execution_id, resposta final), conforme docs/TESTING.md.

## Documentação afetada

`docs/API.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-19. Framework web era decisão em aberto
(`docs/OPEN_QUESTIONS.md`, item 1) — perguntado ao usuário, que escolheu
**FastAPI** (`docs/DECISION_LOG.md`, DEC-009); `fastapi`/`uvicorn`
adicionados a `backend/pyproject.toml` (já estavam instalados no
Python do sistema).

Criado `backend/app/api/`: `app.py` (aplicação FastAPI, handler global
convertendo `ClaudiaoError` para o formato JSON de erro padrão do
projeto, TASK-008), `auth.py` (`get_current_application`, autentica via
header `Authorization: Bearer <api_key>`, reaproveitando
`app.auth.api_keys.authenticate_application`, TASK-011; código de erro
`2002`), `executions.py` (`POST /v1/executions`, autentica e cria uma
`Execution` nova, TASK-020, devolvendo `execution_id`/`status`).

Payload aceito como objeto JSON genérico, sem validação de schema
(TASK-068); execução nunca processada de fato (TASK-069); sem timeout
(TASK-070/071), sem formato final de resposta de sucesso (TASK-072), sem
rastreio de consumo (TASK-073) — nenhuma dessas TASKs implementada aqui.

7 testes novos (3 unitários de extração de token, sem tocar o banco + 4
de integração real via `TestClient`, autenticação e criação de execução
reais). Suíte completa: 543/543 testes aprovados.
