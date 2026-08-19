# TASK-073 — Implementar rastreio de consumo

Status: **Concluída em 2026-08-19**

## Objetivo

Implementar rastreio de consumo, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Aplicações") e `docs/API.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Aplicações" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/API.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-072 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/API.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários e de integração da API para aplicações (payload válido/inválido, timeout, execution_id, resposta final), conforme docs/TESTING.md.

## Documentação afetada

`docs/API.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-19. Criado novo módulo `backend/app/usage/`
(`usage_model.py`): `record_usage(application_id, execution_id, status)`
e `list_usage_for_application(application_id)`, com persistência real em
`usage_records` (`backend/app/db/migrations/0015_usage_records.sql`,
`application_id` com `ON DELETE CASCADE`, `execution_id` como texto sem
FK — `Execution` ainda não é persistida em tabela própria). `POST
/v1/executions` (`backend/app/api/executions.py`) chama `record_usage`
em todo desfecho — sucesso, timeout e falha de modelo/ferramenta —,
gravando `application.id`/`execution.execution_id`/status final.
Requisições rejeitadas antes da autenticação/validação não geram
registro (nunca chegam a criar uma `Execution`).

Escopo deliberadamente mínimo: só o registro de que uma requisição
aconteceu (cobre "número de requisições" de `docs/QUOTAS.md` via
`COUNT(*)`). Medição de tokens/volume, ciclo de renovação, avisos 80/95%
e bloqueio em 100% continuam o sistema de cotas completo — TASK-108 a
TASK-114, explicitamente fora de escopo aqui (`docs/QUOTAS.md` já
atribuía isso a essas TASKs antes desta). `backend/app/README.md`
ganhou uma entrada `usage/` distinta da `quotas/` já prevista (o
"registro mínimo" desta TASK vira a base de dados sobre a qual o sistema
de cotas completo mede/agrega depois).

Com esta TASK, o bloco "Aplicações" (TASK-067 a TASK-073) está completo.

4 testes de integração novos em
`tests/integration/test_usage_model_integration.py` (persistência,
listagem em ordem cronológica, lista vazia, `ON DELETE CASCADE`) mais 3
asserções novas nos testes de integração já existentes de `POST
/v1/executions` (sucesso, falha de modelo, timeout — confirmando o
`status` gravado em cada caso). Suíte completa: 571/571 testes
aprovados, zero pulados (Ollama local verificado rodando antes da
execução).
