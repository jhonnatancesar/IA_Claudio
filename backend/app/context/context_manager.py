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

Esta TASK (TASK-039) acrescenta rastreamento de entidades recentes
(`track_entity`) e de referências implícitas (`set_implicit_reference`/
`resolve_reference`) — "o Claudião deve entender referências como 'esse',
'ele', 'o outro'" (seção 9). `recent_entities` guarda a entidade mais
recente primeiro, sem repetição; `implicit_references` mapeia a palavra de
referência ("esse", "ele") para a entidade que ela resolve no momento.

Esta TASK (TASK-040) acrescenta `record_correction`: registra uma correção
feita pelo usuário ("correções feitas pelo usuário", seção 9) em
`corrections`, em ordem cronológica — histórico simples, sem tentar
reinterpretar `active_topic`/`current_objective` a partir da correção
(isso exigiria entender o conteúdo da correção, fora do escopo desta TASK).

Monitor de janela de contexto e aviso em 80% são TASK-042/TASK-043.
Nenhum desses comportamentos é implementado aqui.
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

    def track_entity(self, entity: str) -> None:
        """Registra `entity` como a mais recentemente mencionada (TASK-039).
        Se `entity` já estiver em `recent_entities`, é movida para o início
        em vez de duplicada — `recent_entities` reflete recência, não
        contagem de menções. Levanta `ValueError` se `entity` for vazia."""
        if not entity or not entity.strip():
            raise ValueError("entity não pode ser vazia")
        if entity in self.recent_entities:
            self.recent_entities.remove(entity)
        self.recent_entities.insert(0, entity)

    def set_implicit_reference(self, reference: str, entity: str) -> None:
        """Associa uma palavra de referência implícita (ex.: "esse", "ele",
        "o outro") à entidade que ela resolve neste momento da conversa
        (TASK-039). Uma nova chamada com a mesma `reference` substitui a
        associação anterior. Levanta `ValueError` se `reference` ou `entity`
        forem vazias."""
        if not reference or not reference.strip():
            raise ValueError("reference não pode ser vazia")
        if not entity or not entity.strip():
            raise ValueError("entity não pode ser vazia")
        self.implicit_references[reference] = entity

    def resolve_reference(self, reference: str) -> str | None:
        """Resolve uma referência implícita para a entidade associada
        (TASK-039), ou `None` se `reference` não tiver associação
        registrada."""
        return self.implicit_references.get(reference)

    def record_correction(self, correction: str) -> None:
        """Registra uma correção feita pelo usuário (TASK-040) em
        `corrections`, em ordem cronológica (mais antiga primeiro). Só
        registra o histórico — aplicar a correção sobre `active_topic`/
        `current_objective` exigiria interpretar seu conteúdo, fora do
        escopo desta TASK. Levanta `ValueError` se `correction` for
        vazia."""
        if not correction or not correction.strip():
            raise ValueError("correction não pode ser vazia")
        self.corrections.append(correction)
