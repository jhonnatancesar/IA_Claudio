# TASK-056 — Implementar evidências/fontes

Status: **Concluída em 2026-08-18**

## Objetivo

Implementar evidências/fontes, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Conhecimento") e `docs/KNOWLEDGE.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Conhecimento" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/KNOWLEDGE.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-055 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/KNOWLEDGE.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários de conhecimento (modelo RAW/PROVISIONAL/CONFIRMED, versionamento, escopo, evidências ou promoção, conforme o caso), conforme docs/TESTING.md.

## Documentação afetada

`docs/KNOWLEDGE.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-18. Criado schema
`backend/app/db/migrations/0009_knowledge_evidence.sql` (colunas
`confidence`/`volatility` em `knowledge`, tabela `knowledge_evidence` com
`ON DELETE CASCADE`), aplicado no PostgreSQL local real. Em
`backend/app/knowledge/knowledge_model.py`: `confidence`/`volatility`
opcionais em `Knowledge`, reaproveitando `Confidence`
(`app.llm.protocol`) e `Volatility` (`app.confidence.volatility`) —
vocabulário já existente, não duplicado.
`set_knowledge_confidence`/`set_knowledge_volatility` definem cada um.
`Evidence`/`add_evidence`/`list_evidence` guardam evidências como texto
livre associado a uma versão — cadastro real de fontes é TASK-059 em
diante.

Exposto na Knowledge Tool: `"SET_CONFIDENCE"`, `"SET_VOLATILITY"`,
`"ADD_EVIDENCE"`, `"LIST_EVIDENCE"`.

22 testes novos (10 unitários de validação + 12 de integração real, entre
modelo e Knowledge Tool). Suíte completa: 456/456 testes aprovados.
