# Conhecimento

Documentação: docs/KNOWLEDGE.md. TASKs: TASK-052 a TASK-058.

Modelo RAW/PROVISIONAL/CONFIRMED, Knowledge Tool, versionamento, escopo GLOBAL/APPLICATION, evidências/fontes, promoção para CONFIRMED, avaliação de utilidade.

- `knowledge_model.py` (TASK-052, TASK-054, TASK-055, TASK-056) —
  `KnowledgeStatus` (`RAW`/`PROVISIONAL`/`CONFIRMED`), `Knowledge`
  (dataclass), `save_knowledge(content, scope_type=GLOBAL, scope_id=None)`,
  `get_knowledge(knowledge_id)`, `advance_knowledge_status(knowledge_id,
  new_status)` — transição mecânica entre estágios, sem decidir quando
  promover (regra de promoção real é TASK-057). Persistência real no
  PostgreSQL local (`backend/app/db/migrations/0006_knowledge.sql` +
  `0007_knowledge_versioning.sql` + `0008_knowledge_scope.sql` +
  `0009_knowledge_evidence.sql`). Sem remoção — conhecimento nunca é
  apagado automaticamente. `create_new_version(knowledge_id, new_content,
  reason)`/`get_current_version(root_id)`/`list_version_history(root_id)`
  (TASK-054) — versionamento: nunca sobrescreve `content`, sempre insere
  linha nova; nova versão sempre começa em `RAW` e herda o escopo da
  anterior. `KnowledgeScope` (`GLOBAL`/`APPLICATION`)/`list_knowledge_for_scope
  (scope_type, scope_id=None)` (TASK-055) — escopo `GLOBAL`/
  `APPLICATION:<id>`, nunca misturando escopos na listagem.
  `set_knowledge_confidence`/`set_knowledge_volatility` (reaproveitando
  `Confidence`/`Volatility` já existentes) e
  `Evidence`/`add_evidence`/`list_evidence` (texto livre; fonte cadastrada
  de verdade é TASK-059+) (TASK-056).
- `promotion_rule.py` (TASK-057) — `is_eligible_for_confirmation
  (knowledge, evidence_count)` (função pura: confiança `HIGH` + pelo
  menos 1 evidência) e `promote_to_confirmed(knowledge_id)` — aplica a
  regra e só então chama `advance_knowledge_status`;
  `KnowledgePromotionNotEligibleError` se não elegível, sem alterar
  nada. Promoção `RAW → PROVISIONAL` não é desta TASK.
- `usefulness.py` (TASK-058) — `is_useful_for_orchestrator(knowledge,
  is_relevant_to_objective)` (função pura): exige `CONFIRMED` +
  relevância para o objetivo atual, recebida já avaliada por quem chama
  (contextual, não deriva do `Knowledge`). Avaliação do orquestrador, não
  uma operação da Knowledge Tool. Com esta TASK, o bloco "Conhecimento"
  (TASK-052 a TASK-058) está completo.

Testes em `tests/integration/test_knowledge_model_integration.py`,
`tests/integration/test_knowledge_versioning_integration.py`,
`tests/integration/test_knowledge_scope_integration.py`,
`tests/integration/test_knowledge_evidence_integration.py`,
`tests/integration/test_knowledge_promotion_rule_integration.py`
(persistência/transições/versionamento/escopo/evidências/promoção reais)
e `tests/unit/test_knowledge_model.py`/`tests/unit/test_knowledge_versioning.py`/
`tests/unit/test_knowledge_scope.py`/`tests/unit/test_knowledge_evidence.py`/
`tests/unit/test_knowledge_promotion_rule.py`/`tests/unit/test_knowledge_usefulness.py`
(validação/regras puras).
