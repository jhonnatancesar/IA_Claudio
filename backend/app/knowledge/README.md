# Conhecimento

Documentação: docs/KNOWLEDGE.md. TASKs: TASK-052 a TASK-058.

Modelo RAW/PROVISIONAL/CONFIRMED, Knowledge Tool, versionamento, escopo GLOBAL/APPLICATION, evidências/fontes, promoção para CONFIRMED, avaliação de utilidade.

- `knowledge_model.py` (TASK-052, TASK-054) — `KnowledgeStatus`
  (`RAW`/`PROVISIONAL`/`CONFIRMED`), `Knowledge` (dataclass),
  `save_knowledge(content)`, `get_knowledge(knowledge_id)`,
  `advance_knowledge_status(knowledge_id, new_status)` — transição
  mecânica entre estágios, sem decidir quando promover (regra de
  promoção real é TASK-057). Persistência real no PostgreSQL local
  (`backend/app/db/migrations/0006_knowledge.sql` +
  `0007_knowledge_versioning.sql`). Sem remoção — conhecimento nunca é
  apagado automaticamente. `create_new_version(knowledge_id, new_content,
  reason)`/`get_current_version(root_id)`/`list_version_history(root_id)`
  (TASK-054) — versionamento: nunca sobrescreve `content`, sempre insere
  linha nova; nova versão sempre começa em `RAW`. Escopo GLOBAL/APPLICATION
  (TASK-055), evidências/fontes (TASK-056) não são desta TASK.

Testes em `tests/integration/test_knowledge_model_integration.py`,
`tests/integration/test_knowledge_versioning_integration.py`
(persistência/transições/versionamento reais) e
`tests/unit/test_knowledge_model.py`/`tests/unit/test_knowledge_versioning.py`
(validação de campos vazios).
