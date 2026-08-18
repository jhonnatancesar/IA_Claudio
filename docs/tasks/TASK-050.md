# TASK-050 — Implementar limite fixo de memória

Status: **Concluída em 2026-08-18**

## Objetivo

Implementar limite fixo de memória, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Memória") e `docs/MEMORY.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Memória" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/MEMORY.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-049 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/MEMORY.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários de memória (persistência, busca, relevância, retenção ou auditoria de remoção, conforme o caso); teste de integração com o banco quando a TASK persistir dados, conforme docs/TESTING.md.

## Documentação afetada

`docs/MEMORY.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-18. Acrescentados `MAX_MEMORIES_PER_OWNER = 500` e
`enforce_memory_limit(owner_type, owner_id, now, max_memories=
MAX_MEMORIES_PER_OWNER)` em `backend/app/memory/retention_policy.py`:
limite fixo de memórias por dono na V1 (seção 11: "fixo na V1, valor exato
a definir durante a implementação da TASK correspondente") — 500 é o valor
escolhido, mesmo espírito de outros limiares já definidos direto em
código sem exigir decisão de arquitetura à parte (`DEFAULT_MAX_STEPS`,
TASK-028). Quando o dono excede o limite, remove as excedentes começando
pelas de menor `relevance_score` (TASK-048) — "remove primeiro as
memórias menos relevantes e menos usadas recentemente".

Auditoria da remoção (TASK-051) não é desta TASK — a remoção aqui não
deixa rastro.

6 testes de integração novos (`enforce_memory_limit` contra o PostgreSQL
local real). Suíte completa: 373/373 testes aprovados.
