# TASK-077 — Implementar retenção/limpeza

Status: **Concluída em 2026-08-21**

## Objetivo

Implementar retenção/limpeza, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Fila") e `docs/QUEUE.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Fila" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/QUEUE.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-076 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/QUEUE.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários e de integração da fila (estados, persistência, retenção), conforme docs/TESTING.md.

## Documentação afetada

`docs/QUEUE.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-21. `delete_queue_item(item_id)` (mecânico,
idempotente) acrescentado a `backend/app/queue/queue_model.py`. Novo
`backend/app/queue/retention_policy.py`, mesma separação mecânico
(model) vs. regra de negócio (rule module) de `app.memory.
retention_policy` (TASK-049):
`is_eligible_for_retention_removal(item, now, max_age_days=7.0)` (função
pura) e `apply_retention_policy(now, max_age_days=7.0)` (aplica de
verdade).

Decisões de design, documentadas no próprio módulo: (1) só itens em
estado terminal (`COMPLETED`/`FAILED`) são elegíveis — um item `PENDING`/
`RUNNING`, mesmo muito antigo, nunca é removido, já que ainda representa
trabalho em aberto, não limpeza de rotina; (2) idade contada a partir de
`finished_at`, não `created_at` — um item que ficou muito tempo
esperando na fila antes de ser processado não é punido por isso; (3)
`DEFAULT_MAX_AGE_DAYS = 7.0` (uma semana), bem mais curto que os 180 dias
da memória (TASK-049) — item de fila é trabalho de processamento já
concluído, não conhecimento de longo prazo a preservar. Valor escolhido
em código, mesmo espírito de outros limiares (`DEFAULT_MAX_STEPS`,
TASK-028; `DEFAULT_MAX_AGE_DAYS` da memória, TASK-049) — não é um
`DEC-0XX` formal.

Com esta TASK, o bloco "Fila" (TASK-074 a TASK-077) está completo.

7 testes unitários novos em `tests/unit/test_queue_retention_policy.py`
(`is_eligible_for_retention_removal` isolada — terminal antigo/recente,
não-terminal nunca elegível mesmo antigo, terminal sem `finished_at`,
limiar customizado) e 7 testes de integração novos em
`tests/integration/test_queue_retention_integration.py`
(`delete_queue_item` real, idempotência, `apply_retention_policy`
removendo/preservando itens, nunca removendo `PENDING`, fila vazia).
Suíte completa: 624/624 testes aprovados, zero pulados (Ollama precisou
ser iniciado manualmente antes da suíte — não estava rodando no início
desta TASK, mesmo já tendo sido iniciado na TASK-076 anterior nesta
mesma sessão).
