"""Monitor de janela de contexto (TASK-042).

`docs/ORCHESTRATOR.md` (seção 9 da especificação mestre): "Configurável pelo
painel; mudança exige reinicialização. Aviso preventivo, discreto, ao
atingir 80% de uso." O painel (TASK-100 em diante) e a persistência de
configuração ainda não existem — `capacity` é recebida como parâmetro
explícito de quem cria o monitor, não lida de configuração salva.

Esta TASK cria só o monitor: quanto da janela já foi usado, e se está
cheia. Emitir o aviso preventivo ao atingir 80% é TASK-043, não
implementado aqui.
"""

from __future__ import annotations

from dataclasses import dataclass


class InvalidContextWindowError(ValueError):
    """Levantado para uma capacidade de janela ou uso inválidos."""


@dataclass(frozen=True)
class ContextWindowMonitor:
    """Acompanha o uso de uma janela de contexto de tamanho fixo
    `capacity`."""

    capacity: int

    def __post_init__(self) -> None:
        if self.capacity <= 0:
            raise InvalidContextWindowError("capacity precisa ser positiva")

    def usage_ratio(self, tokens_used: int) -> float:
        """Fração da janela já usada (`0.0` a `1.0`, podendo passar de
        `1.0` se `tokens_used` exceder `capacity`). Levanta
        `InvalidContextWindowError` se `tokens_used` for negativo."""
        if tokens_used < 0:
            raise InvalidContextWindowError("tokens_used não pode ser negativo")
        return tokens_used / self.capacity

    def is_full(self, tokens_used: int) -> bool:
        """`True` se `tokens_used` já atingiu ou ultrapassou `capacity`."""
        return self.usage_ratio(tokens_used) >= 1.0
