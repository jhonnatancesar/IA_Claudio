# TASK-049 — Implementar política de retenção

Status: **Concluída em 2026-08-18**

## Objetivo

Implementar política de retenção, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Memória") e `docs/MEMORY.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Memória" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/MEMORY.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-048 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/MEMORY.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários de memória (persistência, busca, relevância, retenção ou auditoria de remoção, conforme o caso); teste de integração com o banco quando a TASK persistir dados, conforme docs/TESTING.md.

## Documentação afetada

`docs/MEMORY.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-18. Criado `backend/app/memory/retention_policy.py`:
`is_eligible_for_retention_removal(memory, now, max_age_days=180,
min_relevance=0.05)` (função pura) — elegível quando idade desde
`created_at` passa de `max_age_days` **e** `relevance_score` (TASK-048)
fica abaixo de `min_relevance`, combinando "idade", "baixa relevância" e
"pouco uso" (seção 11) em dois sinais claros. `apply_retention_policy
(owner_type, owner_id, now, ...)` remove de fato as memórias elegíveis
desse dono e retorna os `id`s removidos. Acrescentado `delete_memory
(memory_id)` em `memory_model.py` como suporte.

Limiares padrão (180 dias, 0.05) são a escolha mais simples e defensável,
já que a especificação não define números exatos. Limite máximo por dono
(TASK-050) e auditoria da remoção (TASK-051, "guardar que existiu, quando
e por qual regra") não são desta TASK — a remoção aqui não deixa rastro.

9 testes novos (4 unitários de `is_eligible_for_retention_removal` + 3 de
integração de `apply_retention_policy` + 2 de `delete_memory`). Suíte
completa: 370/370 testes aprovados.
