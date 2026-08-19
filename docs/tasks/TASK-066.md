# TASK-066 — Implementar desbloqueio somente ADMIN

Status: **Concluída em 2026-08-19**

## Objetivo

Implementar desbloqueio somente ADMIN, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Fontes") e `docs/TRUST_GUARDRAILS.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Fontes" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/TRUST_GUARDRAILS.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-065 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/TRUST_GUARDRAILS.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários de fontes/reputação/blacklist para este comportamento específico, conforme docs/TESTING.md.

## Documentação afetada

`docs/TRUST_GUARDRAILS.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-19. Criado `backend/app/sources/unblock_rule.py`:
`admin_unblock_source(source_id, role, responsible, reason)`, que
reaproveita `app.auth.roles.require_admin` (TASK-010, mesmo código de
erro `FORBIDDEN_ADMIN_ONLY`, 2001) em vez de duplicar lógica de
autorização — levanta `ClaudiaoError` antes de tocar qualquer estado se
`role` não for `ADMIN`. "Se o agente bloquear, ele não pode desbloquear
sozinho — somente o `ADMIN`" (seção 14/15) foi lido como desbloqueio
exigindo `ADMIN` sempre, não só quando foi o agente que bloqueou. Só
então chama `unblock_source` (TASK-064, `origin=ADMIN`).

Com esta TASK, o bloco "Fontes" (TASK-059 a TASK-066) está completo.

7 testes novos (2 unitários de rejeição de papel, antes de tocar o banco
+ 5 de integração real). Suíte completa: 536/536 testes aprovados.
