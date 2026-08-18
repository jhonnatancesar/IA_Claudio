# Context Manager

Documentação: docs/ORCHESTRATOR.md. TASKs: TASK-037 a TASK-043.

Assunto principal, entidades recentes, objetivo atual, últimas ações, referências implícitas, correções, troca de assunto e monitor de janela de contexto.

- `context_manager.py` (TASK-037) — `ContextManager` (dataclass): uma
  instância por conversa, com `conversation_id`, `active_topic`,
  `recent_entities`, `current_objective`, `recent_actions`,
  `implicit_references`, `corrections`. `ContextManager.new(conversation_id)`
  cria a instância vazia. Só o modelo de dados — active topic/troca de
  assunto (TASK-038/TASK-041), rastreamento de entidades/referências
  (TASK-039), correção (TASK-040) e monitor de janela de contexto
  (TASK-042/TASK-043) não são desta TASK.

Testes em `tests/unit/test_context_manager.py`.
