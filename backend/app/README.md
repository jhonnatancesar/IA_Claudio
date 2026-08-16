# app/

Módulos do núcleo do Claudião, um por componente da arquitetura descrita em
`docs/ARCHITECTURE.md`:

- `api/` — API para aplicações externas
- `auth/` — autenticação e autorização
- `orchestrator/` — orquestrador determinístico
- `policies/` — Policy Engine (ExecutionPolicy)
- `context/` — Context Manager
- `planner/` — Planner (planejamento/replanejamento)
- `confidence/` — Confidence Engine
- `guardrails/` — Guardrails
- `llm/` — abstração LocalLLMProvider e protocolo JSON
- `llm/providers/` — implementações concretas (OllamaProvider na V1)
- `memory/` — memória persistente
- `knowledge/` — conhecimento (RAW/PROVISIONAL/CONFIRMED)
- `sources/` — fontes, reputação e blacklist
- `tools/` — Tool Registry (Memory, Knowledge, Web Search, File, Database, API Tool)
- `queue/` — fila FIFO
- `observability/` — logging, Execution Trace, métricas
- `quotas/` — cotas de consumo
- `panel/` — painel web (read-only e administrativo)
- `backup/` — backup e restore
- `updater/` — atualização via Git e rollback
- `db/` — persistência PostgreSQL e migrations

Cada diretório tem um `README.md` próprio com a documentação e as TASKs
correspondentes. Nenhum código foi implementado ainda.
