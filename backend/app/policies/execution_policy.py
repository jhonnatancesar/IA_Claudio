"""`ExecutionPolicy` (TASK-022).

Política que governa como uma execução roda — enviada pela aplicação
(docs/API.md; seção 24 da especificação mestre: "contexto, tipo de uso,
política, pesquisa, timeout, limites") ou aplicada por padrão ao chat (seção
18.1: pesquisa não pré-autorizada, pedida por vez; seção 30: sem timeout
fixo no chat).

Só o modelo de dados e sua validação — quem de fato aplica a política durante
uma execução é o `ExecutionOrchestrator` (TASK-023) e as TASKs de limite
(`max_steps`: TASK-028; detecção de loop: TASK-029).
"""

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_MAX_STEPS = 10  # seção 30 da especificação: "max_steps inicial sugerido: 10"


class InvalidExecutionPolicyError(ValueError):
    """Levantado quando os valores da política violam as regras da
    especificação (ex.: timeout no chat, `max_steps` não positivo)."""


@dataclass(frozen=True)
class ExecutionPolicy:
    """Política declarada para uma execução."""

    web_search_allowed: bool
    max_steps: int = DEFAULT_MAX_STEPS
    timeout_seconds: float | None = None

    def __post_init__(self) -> None:
        if self.max_steps <= 0:
            raise InvalidExecutionPolicyError("max_steps deve ser positivo")
        if self.timeout_seconds is not None and self.timeout_seconds <= 0:
            raise InvalidExecutionPolicyError(
                "timeout_seconds deve ser positivo quando definido"
            )

    @classmethod
    def for_chat(
        cls, *, web_search_allowed: bool = False, max_steps: int = DEFAULT_MAX_STEPS
    ) -> "ExecutionPolicy":
        """Política padrão do chat: sem timeout fixo (seção 30 — "No chat não
        haverá timeout fixo") e pesquisa não pré-autorizada por padrão (seção
        18.1 — no chat, a autorização de pesquisa é pedida por vez, não
        declarada de antemão nesta política)."""
        return cls(
            web_search_allowed=web_search_allowed,
            max_steps=max_steps,
            timeout_seconds=None,
        )

    @classmethod
    def for_application(
        cls,
        *,
        timeout_seconds: float,
        web_search_allowed: bool = False,
        max_steps: int = DEFAULT_MAX_STEPS,
    ) -> "ExecutionPolicy":
        """Política de uma aplicação: `timeout_seconds` é obrigatório (seção
        26 — "O timeout é definido pela própria aplicação")."""
        if timeout_seconds is None:
            raise InvalidExecutionPolicyError(
                "aplicações precisam definir timeout_seconds"
            )
        return cls(
            web_search_allowed=web_search_allowed,
            max_steps=max_steps,
            timeout_seconds=timeout_seconds,
        )
