# TASK-014 — Criar interface LocalLLMProvider

Status: **Concluída em 2026-08-16**

## Objetivo

Criar interface LocalLLMProvider, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "LLM") e `docs/ARCHITECTURE.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "LLM" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/ARCHITECTURE.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-013 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/ARCHITECTURE.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários do provider e do protocolo JSON (parser/validator contra JSON malformado ou fora do contrato), conforme docs/TESTING.md.

## Documentação afetada

`docs/ARCHITECTURE.md`, `docs/tasks/README.md`, `backend/app/llm/README.md`

## Encerramento

Concluída em 2026-08-16. Criado `backend/app/llm/provider.py`:
`LocalLLMProvider` (ABC, `complete()`/`is_available()`), `CompletionRequest`/
`CompletionResponse` (dataclasses frozen), `LocalLLMProviderError`. Só a
interface — sem implementação concreta (TASK-015) e sem o protocolo JSON por
etapa (TASK-016/TASK-017). 7 testes unitários novos (instanciação direta da
ABC falha, subclasse incompleta falha, defaults do request, imutabilidade,
provider fake completo e indisponível). Suíte completa: 91/91 testes
aprovados.
