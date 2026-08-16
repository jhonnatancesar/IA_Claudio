# Roadmap

Fonte: seção 50 (backlog macro) e seção 51 (TASKs ordenadas) da especificação mestre.

O roadmap é organizado em 11 fases sequenciais. Dentro de cada fase, as TASKs também
são sequenciais (cada uma depende da anterior, salvo indicação em contrário no próprio
arquivo da TASK). Ver `docs/BACKLOG.md` para a lista completa de TASKs por bloco.

| Fase | Nome | TASKs | Conteúdo |
|---|---|---|---|
| 0 | Fundação | TASK-001 a TASK-013 | estrutura do projeto, configuração, PostgreSQL, catálogo de erros, logging, autenticação |
| 1 | LLM local | TASK-014 a TASK-019 | `LocalLLMProvider`, Ollama, protocolo JSON, prompt-base, parser/validator |
| 2 | Núcleo agente | TASK-020 a TASK-043 | orquestrador, policies, planejamento, replanejamento, contexto, confidence engine, guardrails |
| 3 | Persistência inteligente | TASK-044 a TASK-066 | memória, conhecimento, versionamento, fontes, reputação |
| 4 | API de aplicações | TASK-067 a TASK-073 | API key, payload, validação, timeout, JSON final, `execution_id` |
| 5 | Fila e observabilidade | TASK-074 a TASK-087 | FIFO, traces, painel read-only, métricas básicas, marco utilizável inicial |
| 6 | Ferramentas | TASK-088 a TASK-100 | Web Search, File, Database, API Tool |
| 7 | Chat | TASK-101 a TASK-107 | terminal, web, streaming, contexto, histórico |
| 8 | Cotas e administração | TASK-108 a TASK-122 | cotas, painel completo, usuários, providers, manutenção |
| 9 | Operação segura | TASK-123 a TASK-137 | backup, restore, updates, rollback, health checks |
| 10 | Qualidade | TASK-138 a TASK-147 | testes, cenários, métricas, checklist V1 |

> Nota: a fase 2 do backlog macro (seção 50) agrupa Orquestração, Confiança/guardrails
> e Contexto (TASK-020 a TASK-043); a fase 3 agrupa Memória, Conhecimento e Fontes
> (TASK-044 a TASK-066); a fase 5 agrupa Fila, Observabilidade inicial e o bloco
> "Marco utilizável inicial" (TASK-074 a TASK-087). `docs/BACKLOG.md` preserva os
> nomes de subgrupo originais da seção 51 para referência mais granular.

## Marcos

- **TASK-087 — primeiro Claudião utilizável.** Fecha o mínimo utilizável seguro
  (ver `docs/V1_SCOPE.md`). A partir daqui o Claudião é considerado utilizável em
  produção controlada.
- **TASK-147 — V1 completa.** Fecha o checklist de todos os itens planejados da V1.

## Ordem recomendada de início

Conforme a seção "Ponto de partida manual" da especificação: TASK-001 → TASK-002 →
TASK-003 → TASK-004 → TASK-005 → TASK-006 → TASK-007 → TASK-008, e só então
TASK-009 em diante. O primeiro objetivo técnico concreto é chegar ao bloco do LLM
(TASK-014 a TASK-019) com fundação, erros, autenticação e persistência mínimas já
organizadas. Não começar pelo frontend nem pelo Web Search.
