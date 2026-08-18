# TASK-057 — Implementar regra de promoção para CONFIRMED

Status: **Concluída em 2026-08-18**

## Objetivo

Implementar regra de promoção para CONFIRMED, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Conhecimento") e `docs/KNOWLEDGE.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Conhecimento" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/KNOWLEDGE.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-056 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/KNOWLEDGE.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários de conhecimento (modelo RAW/PROVISIONAL/CONFIRMED, versionamento, escopo, evidências ou promoção, conforme o caso), conforme docs/TESTING.md.

## Documentação afetada

`docs/KNOWLEDGE.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-18. Criado `backend/app/knowledge/promotion_rule.py`:
`is_eligible_for_confirmation(knowledge, evidence_count)` (função pura)
— exige status `PROVISIONAL`, confiança `HIGH` e pelo menos
`MIN_EVIDENCE_COUNT_FOR_CONFIRMATION` (`1`) evidência registrada;
critério mais simples e defensável, já que a especificação não detalha
uma fórmula. `promote_to_confirmed(knowledge_id)` busca o conhecimento e
suas evidências, verifica elegibilidade e só então chama
`advance_knowledge_status` (TASK-052); `KnowledgePromotionNotEligibleError`
sem alterar nada quando não elegível.

Promoção `RAW → PROVISIONAL` não é desta TASK. Reputação real de fontes
(TASK-059+) pode refinar o critério depois. Exposta na Knowledge Tool
como `"PROMOTE_TO_CONFIRMED"`, distinta de `"ADVANCE"` (que continua sem
julgamento).

14 testes novos (6 unitários de `is_eligible_for_confirmation`, função
pura + 8 de integração real, entre modelo e Knowledge Tool). Suíte
completa: 470/470 testes aprovados.
