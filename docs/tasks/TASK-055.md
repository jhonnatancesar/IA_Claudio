# TASK-055 — Implementar escopo GLOBAL/APPLICATION

Status: **Concluída em 2026-08-18**

## Objetivo

Implementar escopo GLOBAL/APPLICATION, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Conhecimento") e `docs/KNOWLEDGE.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Conhecimento" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/KNOWLEDGE.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-054 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/KNOWLEDGE.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários de conhecimento (modelo RAW/PROVISIONAL/CONFIRMED, versionamento, escopo, evidências ou promoção, conforme o caso), conforme docs/TESTING.md.

## Documentação afetada

`docs/KNOWLEDGE.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-18. Criado schema
`backend/app/db/migrations/0008_knowledge_scope.sql` (colunas
`scope_type`/`scope_id` em `knowledge`, `CHECK` garantindo `scope_id`
presente só quando `scope_type = 'APPLICATION'`), aplicado no PostgreSQL
local real. Em `backend/app/knowledge/knowledge_model.py`:
`KnowledgeScope` (`GLOBAL`/`APPLICATION`), `scope_type`/`scope_id` em
`Knowledge`/`save_knowledge` (`GLOBAL` por padrão), `create_new_version`
agora herda o escopo da versão anterior, `list_knowledge_for_scope
(scope_type, scope_id=None)` lista as versões atuais de um escopo sem
misturar escopos diferentes. Nenhuma função troca o escopo de um
conhecimento existente — "não pode ser promovido automaticamente para
global" satisfeito por omissão. Exposto na Knowledge Tool:
`scope_type`/`scope_id` opcionais em `SAVE`, nova operação
`"LIST_SCOPE"`.

Evidências/fontes (TASK-056) não são desta TASK.

15 testes novos (7 unitários de validação + 8 de integração real, entre
modelo e Knowledge Tool). Suíte completa: 434/434 testes aprovados.
