# TASK-007 — Criar catálogo interno de erros

Status: **Concluída em 2026-08-16**

## Objetivo

Fechar o catálogo inicial de erros, antes da API, conforme a seção "Ponto de partida
manual" da especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`)
e `docs/ERROR_CATALOG.md` (faixas de código 1000–9999).

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Fundação" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/ERROR_CATALOG.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-006 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/ERROR_CATALOG.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários do componente correspondente (config, schema, logging ou catálogo de erros), conforme docs/TESTING.md. Estrutura pura de diretório (sem lógica) não exige teste automatizado.

## Documentação afetada

`docs/ERROR_CATALOG.md`, `docs/tasks/README.md`, `backend/app/errors/README.md`

## Encerramento

Concluída em 2026-08-16. Criado `backend/app/errors/catalog.py`: `ErrorDomain`
(9 faixas de 1000 em 1000, seção 36 da especificação), `ErrorDefinition`,
`register_error()` (valida faixa e unicidade), `get_error()`, `domain_for_code()`.
Catálogo seed com 3 erros da fundação (`MISSING_REQUIRED_FIELD` 1001,
`INVALID_FIELD_VALUE` 1002, `UNKNOWN_INTERNAL_ERROR` 9000) — nenhum código de
domínios de TASKs futuras foi inventado antecipadamente. 12 testes unitários
novos em `tests/unit/test_error_catalog.py` (resolução de domínio por faixa,
rejeição de código fora da faixa, rejeição de duplicata, consulta, erros seed).
Suíte completa: 31/31 testes aprovados. Formato de resposta JSON padrão que usa
esse catálogo é escopo da TASK-008, não implementado aqui.
