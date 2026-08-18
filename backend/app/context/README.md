# Context Manager

Documentação: docs/ORCHESTRATOR.md. TASKs: TASK-037 a TASK-043.

Assunto principal, entidades recentes, objetivo atual, últimas ações, referências implícitas, correções, troca de assunto e monitor de janela de contexto.

- `context_manager.py` (TASK-037, TASK-038, TASK-039) — `ContextManager`
  (dataclass): uma instância por conversa, com `conversation_id`,
  `active_topic`, `recent_entities`, `current_objective`, `recent_actions`,
  `implicit_references`, `corrections`. `ContextManager.new(conversation_id)`
  cria a instância vazia. `set_active_topic(topic)` (TASK-038) define o
  assunto principal, substituindo o anterior — só um por vez.
  `track_entity(entity)` (TASK-039) registra a entidade mais recente em
  `recent_entities` (recência, sem duplicar). `set_implicit_reference
  (reference, entity)`/`resolve_reference(reference)` (TASK-039) associam e
  consultam a entidade que uma referência ("esse", "ele") resolve agora.
  Detectar troca de assunto real (TASK-041), correção (TASK-040) e monitor
  de janela de contexto (TASK-042/TASK-043) não são desta TASK.

Testes em `tests/unit/test_context_manager.py`.
