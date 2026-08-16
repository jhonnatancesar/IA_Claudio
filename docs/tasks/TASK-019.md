# TASK-019 — Criar composição dinâmica de prompt/contexto

Status: **Concluída em 2026-08-16**

## Objetivo

Criar composição dinâmica de prompt/contexto, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "LLM") e `docs/ARCHITECTURE.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "LLM" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/ARCHITECTURE.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-018 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/ARCHITECTURE.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários do provider e do protocolo JSON (parser/validator contra JSON malformado ou fora do contrato), conforme docs/TESTING.md.

## Documentação afetada

`docs/ARCHITECTURE.md`, `docs/tasks/README.md`, `backend/app/llm/README.md`

## Encerramento

Concluída em 2026-08-16. Criado `backend/app/llm/prompt_composer.py`:
`compose_prompt(execution_id, objective, history=None)` monta o prompt
completo (base + pedido atual + histórico de etapas desta execução via
`StepRecord`). Memória, conhecimento e o Context Manager entre conversas
(TASK-037/TASK-044/TASK-052 em diante) ainda não existem — não incluídos.

Corrigida também uma regressão descoberta ao testar: `ModelStep.to_json()`
(TASK-016) não usava `ensure_ascii=False`, escapando acentos em `reason` como
`\uXXXX` em vez de UTF-8 legível — problema real para um protocolo em PT-BR.
9 testes unitários novos da composição + 1 teste de regressão do fix. Suíte
completa: 146/146 testes aprovados.

**Com esta TASK, o bloco "LLM" (TASK-014 a TASK-019) está completo.**
