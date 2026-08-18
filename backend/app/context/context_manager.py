"""Modelo de `ContextManager` (TASK-037), com assunto principal (TASK-038).

"Contexto de conversa" (docs/ORCHESTRATOR.md, seção 9 da especificação
mestre): o `ContextManager` mantém assunto principal, entidades recentes,
objetivo atual, últimas ações, referências implícitas e correções feitas
pelo usuário — uma instância por conversa.

TASK-037 criou só o modelo de dados e sua identidade (`conversation_id`),
com os campos previstos já presentes (vazios/`None`) para as TASKs
seguintes construírem em cima, mesmo padrão usado por `Execution`
(TASK-020). Esta TASK (TASK-038) acrescenta `set_active_topic`: "A V1
mantém um assunto principal por vez" — trocar o assunto substitui o
anterior, não acumula uma lista. Detectar *quando* uma troca de assunto
real aconteceu (para então trocar e limpar referências antigas) é
TASK-041, não implementado aqui — este método só troca o valor, dado que
quem chama já decidiu que deve trocar.

Rastreamento de entidades/referências implícitas é TASK-039, correção de
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

    def set_active_topic(self, topic: str) -> None:
        """Define o assunto principal da conversa (TASK-038), substituindo
        qualquer assunto anterior — a V1 mantém só um assunto principal por
        vez. Levanta `ValueError` se `topic` for vazio."""
        if not topic or not topic.strip():
            raise ValueError("active_topic não pode ser vazio")
        self.active_topic = topic
