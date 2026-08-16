# Claudião

Agente inteligente **local, genérico e reutilizável**, cujo raciocínio principal roda
no próprio servidor, sem depender de OpenAI, Gemini, Claude, Groq, OpenRouter ou
qualquer outra IA externa para pensar normalmente. Internet, APIs e outras
integrações são **ferramentas** — nunca fallback de inteligência.

> Projeto novo e separado do AIShoppingAgent. Não reutiliza código nem regras de
> negócio daquele sistema — só sua organização de repositório serviu de referência.

## Status

Repositório organizado (estrutura, documentação e planejamento das TASKs).
**TASK-001** a **TASK-008** concluídas — bloco "Fundação" completo (estrutura,
config, PostgreSQL, schema inicial, logging local e no PostgreSQL, catálogo de
erros e formato JSON padrão de erro). Nenhuma outra funcionalidade foi
implementada ainda.

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

**TASK-009 — Criar autenticação de usuários**
([docs/tasks/TASK-009.md](docs/tasks/TASK-009.md)).
