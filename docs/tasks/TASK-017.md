# TASK-017 — Criar validação dos JSONs internos

Status: **Concluída em 2026-08-16**

## Objetivo

Criar validação dos JSONs internos, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "LLM") e `docs/ARCHITECTURE.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "LLM" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/ARCHITECTURE.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-016 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/ARCHITECTURE.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários do provider e do protocolo JSON (parser/validator contra JSON malformado ou fora do contrato), conforme docs/TESTING.md.

## Documentação afetada

`docs/ARCHITECTURE.md`, `docs/ERROR_CATALOG.md`, `docs/tasks/README.md`,
`backend/app/llm/README.md`

## Encerramento

Concluída em 2026-08-16. Criado `backend/app/llm/protocol_validator.py`:
`validate_step(raw) -> ModelStep` decodifica via `ModelStep.from_json`
(TASK-016) e adiciona checagens semânticas (`execution_id` em formato UUID,
`reason` não-vazio); qualquer falha vira `ClaudiaoError` com o novo código
`4001` (`INVALID_MODEL_STEP`, HTTP 502, faixa `MODEL_ORCHESTRATOR`). Corrigido
também um bug de regressão em `protocol.py` (TASK-016): `parameters`
não-objeto (lista, string) escapava como `ValueError`/`TypeError` genérico em
vez de `ProtocolDecodeError`. 2 testes de regressão para o fix + 8 testes
novos do validador. Suíte completa: 126/126 testes aprovados.
