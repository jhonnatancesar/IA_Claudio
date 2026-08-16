# Claudião

Agente inteligente **local, genérico e reutilizável**, cujo raciocínio principal roda
no próprio servidor, sem depender de OpenAI, Gemini, Claude, Groq, OpenRouter ou
qualquer outra IA externa para pensar normalmente. Internet, APIs e outras
integrações são **ferramentas** — nunca fallback de inteligência.

> Projeto novo e separado do AIShoppingAgent. Não reutiliza código nem regras de
> negócio daquele sistema — só sua organização de repositório serviu de referência.

## Status

Repositório organizado (estrutura, documentação e planejamento das TASKs).
**TASK-001** a **TASK-010** concluídas — bloco "Fundação" completo, autenticação
de usuários e autorização por papel (ADMIN/USER) funcionando. Nenhuma outra
funcionalidade foi implementada ainda. Ver [docs/HANDOFF.md](docs/HANDOFF.md)
para o estado detalhado do projeto.

## Documentação

- [docs/](docs/) — arquitetura, escopo, memória, conhecimento, confiança/guardrails,
  ferramentas, API, segurança, observabilidade, cotas, painel, operação, backup,
  updater, banco de dados e testes.
- [docs/tasks/](docs/tasks/) — TASK-001 a TASK-147, uma por arquivo.
- [docs/BACKLOG.md](docs/BACKLOG.md) e [docs/ROADMAP.md](docs/ROADMAP.md) — TASKs
  agrupadas por bloco e por fase.
- [docs/DECISION_LOG.md](docs/DECISION_LOG.md) — decisões tomadas após a
  especificação mestre.
- [docs/OPEN_QUESTIONS.md](docs/OPEN_QUESTIONS.md) — pontos ainda em aberto.

## Marcos

- **TASK-087** — primeiro Claudião utilizável em produção controlada.
- **TASK-147** — V1 completa.

## Próxima TASK

**TASK-011 — Criar autenticação de aplicações via API key**
([docs/tasks/TASK-011.md](docs/tasks/TASK-011.md)).
