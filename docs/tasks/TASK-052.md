# TASK-052 — Criar modelo RAW/PROVISIONAL/CONFIRMED

Status: **Concluída em 2026-08-18**

## Objetivo

Criar modelo RAW/PROVISIONAL/CONFIRMED, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Conhecimento") e `docs/KNOWLEDGE.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Conhecimento" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/KNOWLEDGE.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-051 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/KNOWLEDGE.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários de conhecimento (modelo RAW/PROVISIONAL/CONFIRMED, versionamento, escopo, evidências ou promoção, conforme o caso), conforme docs/TESTING.md.

## Documentação afetada

`docs/KNOWLEDGE.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-18. Criado schema
`backend/app/db/migrations/0006_knowledge.sql` (tabela `knowledge`: `id`,
`status`, `content`, `created_at`, `updated_at`), aplicado no PostgreSQL
local real. Criado `backend/app/knowledge/knowledge_model.py`:
`KnowledgeStatus` (`RAW`/`PROVISIONAL`/`CONFIRMED`), `Knowledge`
(dataclass), `save_knowledge(content)` (sempre começa em `RAW`),
`get_knowledge(knowledge_id)`, `advance_knowledge_status(knowledge_id,
new_status)` — transição mecânica validada por um grafo (`RAW →
PROVISIONAL → CONFIRMED`, um passo por vez, nunca pulando/voltando/
repetindo), mesmo padrão de `Execution` (TASK-020).

Sem função de remoção — conhecimento nunca é apagado automaticamente
(diferente de `app.memory.memory_model`, TASK-044). Decidir *quando*
promover (com base em evidências/fontes) é a regra de promoção,
TASK-057, não implementada aqui. Knowledge Tool (TASK-053), versionamento
(TASK-054), escopo GLOBAL/APPLICATION (TASK-055) e evidências/fontes
(TASK-056) também não são desta TASK.

12 testes novos (3 unitários de validação/enum + 9 de integração real).
Suíte completa: 391/391 testes aprovados.
