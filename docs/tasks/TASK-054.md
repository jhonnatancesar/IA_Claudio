# TASK-054 — Implementar versionamento de conhecimento

Status: **Concluída em 2026-08-18**

## Objetivo

Implementar versionamento de conhecimento, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Conhecimento") e `docs/KNOWLEDGE.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Conhecimento" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/KNOWLEDGE.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-053 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/KNOWLEDGE.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários de conhecimento (modelo RAW/PROVISIONAL/CONFIRMED, versionamento, escopo, evidências ou promoção, conforme o caso), conforme docs/TESTING.md.

## Documentação afetada

`docs/KNOWLEDGE.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-18. Criado schema
`backend/app/db/migrations/0007_knowledge_versioning.sql` (colunas
`root_id`/`version`/`is_current`/`previous_version_id`/`change_reason` em
`knowledge`, índice único parcial garantindo uma única versão atual por
linhagem), aplicado no PostgreSQL local real. Em
`backend/app/knowledge/knowledge_model.py`: `create_new_version
(knowledge_id, new_content, reason)` — insere uma linha nova (nunca
sobrescreve `content`), marca a anterior como não-atual na mesma
transação, exige que `knowledge_id` seja a versão atual
(`KnowledgeVersionConflictError` caso contrário); a nova versão sempre
começa em `RAW`. `get_current_version(root_id)`/`list_version_history
(root_id)` consultam a linhagem. Exposta na Knowledge Tool
(`backend/app/tools/knowledge_tool.py`) como nova operação
`"NEW_VERSION"`.

Preservar fontes (TASK-056) não é desta TASK.

17 testes novos (5 unitários de validação + 12 de integração real, entre
modelo e Knowledge Tool). Suíte completa: 419/419 testes aprovados.
