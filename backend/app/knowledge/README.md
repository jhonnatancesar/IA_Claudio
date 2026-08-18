# Conhecimento

Documentação: docs/KNOWLEDGE.md. TASKs: TASK-052 a TASK-058.

Modelo RAW/PROVISIONAL/CONFIRMED, Knowledge Tool, versionamento, escopo GLOBAL/APPLICATION, evidências/fontes, promoção para CONFIRMED, avaliação de utilidade.

- `knowledge_model.py` (TASK-052) — `KnowledgeStatus`
  (`RAW`/`PROVISIONAL`/`CONFIRMED`), `Knowledge` (dataclass),
  `save_knowledge(content)`, `get_knowledge(knowledge_id)`,
  `advance_knowledge_status(knowledge_id, new_status)` — transição
  mecânica entre estágios, sem decidir quando promover (regra de
  promoção real é TASK-057). Persistência real no PostgreSQL local
  (`backend/app/db/migrations/0006_knowledge.sql`). Sem remoção — TASK-052
  não tem `delete_knowledge`, conhecimento nunca é apagado
  automaticamente. Knowledge Tool (TASK-053), versionamento (TASK-054),
  escopo GLOBAL/APPLICATION (TASK-055), evidências/fontes (TASK-056) não
  são desta TASK.

Testes em `tests/integration/test_knowledge_model_integration.py`
(persistência/transições reais) e `tests/unit/test_knowledge_model.py`
(enum, validação de `content` vazio).
