# Claudião

Agente inteligente **local, genérico e reutilizável**, cujo raciocínio principal roda
no próprio servidor, sem depender de OpenAI, Gemini, Claude, Groq, OpenRouter ou
qualquer outra IA externa para pensar normalmente. Internet, APIs e outras
integrações são **ferramentas** — nunca fallback de inteligência.

> Projeto novo e separado do AIShoppingAgent. Não reutiliza código nem regras de
> negócio daquele sistema — só sua organização de repositório serviu de referência.

## Status

Repositório organizado (estrutura, documentação e planejamento das TASKs).
**TASK-001** a **TASK-074** concluídas — blocos "Fundação", "Segurança e
identidade", "LLM", "Orquestração", "Confiança e guardrails", "Contexto",
"Memória", "Conhecimento", "Fontes" e "Aplicações" completos (API local
FastAPI, validação de payload, execução síncrona, timeout com erro
específico, resposta JSON final e rastreio de consumo); bloco "Fila e
observabilidade" iniciado (fila FIFO em memória).
Ver
[docs/HANDOFF.md](docs/HANDOFF.md) para o estado detalhado do projeto.

## Documentação

- [docs/HANDOFF.md](docs/HANDOFF.md) — estado vivo do projeto, atualizado a cada
  10 TASKs concluídas; ponto de partida para retomar o trabalho numa sessão nova.
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

**TASK-075 — Persistir fila no PostgreSQL**
([docs/tasks/TASK-075.md](docs/tasks/TASK-075.md)).
