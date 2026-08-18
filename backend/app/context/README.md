# Context Manager

Documentação: docs/ORCHESTRATOR.md. TASKs: TASK-037 a TASK-043.

Assunto principal, entidades recentes, objetivo atual, últimas ações, referências implícitas, correções, troca de assunto e monitor de janela de contexto.

- `context_manager.py` (TASK-037 a TASK-041) — `ContextManager`
  (dataclass): uma instância por conversa, com `conversation_id`,
  `active_topic`, `recent_entities`, `current_objective`, `recent_actions`,
  `implicit_references`, `corrections`. `ContextManager.new(conversation_id)`
  cria a instância vazia. `set_active_topic(topic)` (TASK-038) define o
  assunto principal, substituindo o anterior — só um por vez.
  `track_entity(entity)` (TASK-039) registra a entidade mais recente em
  `recent_entities` (recência, sem duplicar). `set_implicit_reference
  (reference, entity)`/`resolve_reference(reference)` (TASK-039) associam e
  consultam a entidade que uma referência ("esse", "ele") resolve agora.
  `record_correction(correction)` (TASK-040) registra uma correção do
  usuário em `corrections`, em ordem cronológica. `detect_topic_switch
  (new_topic)` (TASK-041) decide se `new_topic` é uma troca real (string
  diferente do assunto atual) e, se sim, troca e limpa
  `recent_entities`/`implicit_references`.
- `context_window.py` (TASK-042) — `ContextWindowMonitor(capacity)`,
  `usage_ratio(tokens_used)`, `is_full(tokens_used)`. `capacity` é recebida
  como parâmetro explícito — configuração via painel não existe ainda.
  Aviso preventivo em 80% de uso é TASK-043.

Com TASK-042, faltam só TASK-043 para o bloco "Contexto" (TASK-037 a
TASK-043) estar completo.

Testes em `tests/unit/test_context_manager.py`, `tests/unit/test_context_window.py`.
