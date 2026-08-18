"""Modelo de `ContextManager` (TASK-037).

"Contexto de conversa" (docs/ORCHESTRATOR.md, seção 9 da especificação
mestre): o `ContextManager` mantém assunto principal, entidades recentes,
objetivo atual, últimas ações, referências implícitas e correções feitas
pelo usuário — uma instância por conversa.

Esta TASK cria só o modelo de dados e sua identidade (`conversation_id`),
com os campos previstos já presentes (vazios/`None`) para as TASKs
seguintes construírem em cima, mesmo padrão usado por `Execution`
(TASK-020): active topic e troca de assunto são TASK-038/TASK-041,
rastreamento de entidades/referências implícitas é TASK-039, correção de
contexto é TASK-040, monitor de janela de contexto e aviso em 80% são
TASK-042/TASK-043. Nenhum desses comportamentos é implementado aqui.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ContextManager:
    """Contexto de uma conversa em andamento."""

    conversation_id: str
    active_topic: str | None = None
    recent_entities: list[str] = field(default_factory=list)
    current_objective: str | None = None
    recent_actions: list[str] = field(default_factory=list)
    implicit_references: dict[str, str] = field(default_factory=dict)
    corrections: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.conversation_id or not self.conversation_id.strip():
            raise ValueError("conversation_id não pode ser vazio")

    @classmethod
    def new(cls, conversation_id: str) -> "ContextManager":
        """Cria um `ContextManager` vazio para `conversation_id`, sem assunto,
        entidades, objetivo, ações, referências ou correções registradas
        ainda."""
        return cls(conversation_id=conversation_id)
