"""Cancelamento externo/interno (TASK-030).

`CancellationToken` é um sinalizador de cancelamento cooperativo: quem inicia
uma execução guarda uma referência e chama `cancel()` de fora (cancelamento
**externo** — ex.: usuário desiste, ou o timeout da aplicação estoura,
docs/API.md/seção 26 — o erro JSON específico desse caso é TASK-071, não
implementado aqui); o `ExecutionOrchestrator` checa `is_cancelled` entre
etapas e interrompe o ciclo (isso cobre também o cancelamento **interno**: o
próprio código do orquestrador pode chamar `token.cancel(...)` antes de
retornar o controle, pelo mesmo mecanismo).

Sem threads/async na V1 — é só um objeto com estado, checado de forma
síncrona pelo laço do orquestrador entre uma etapa e outra.
"""

from __future__ import annotations


class CancellationToken:
    """Sinalizador de cancelamento cooperativo, compartilhado entre quem
    inicia uma execução e o `ExecutionOrchestrator` que a processa."""

    def __init__(self) -> None:
        self._cancelled = False
        self.reason: str | None = None

    def cancel(self, reason: str = "cancelado") -> None:
        """Marca o token como cancelado. Chamadas repetidas mantêm o motivo
        da primeira chamada."""
        if not self._cancelled:
            self._cancelled = True
            self.reason = reason

    @property
    def is_cancelled(self) -> bool:
        return self._cancelled


class ExecutionCancelledError(RuntimeError):
    """Levantado quando o `ExecutionOrchestrator` encontra um
    `CancellationToken` já cancelado antes/durante uma etapa. Não é um erro
    do catálogo (`ClaudiaoError`) — cancelamento é uma parada deliberada, não
    uma falha; o mapeamento para um erro de aplicação específico (ex.:
    timeout) é escopo de TASKs futuras (TASK-071)."""
