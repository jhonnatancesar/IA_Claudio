"""Modelo de `Execution` (TASK-020).

Representa o ciclo de vida de uma execução do orquestrador (docs/ARCHITECTURE.md,
seção "Orquestrador"). Só o modelo de dados e as transições de estado válidas —
não gera `execution_id` (isso é TASK-021), não decide política (TASK-022), não
executa nada de verdade (`ExecutionOrchestrator` é TASK-023), não implementa
`max_steps`/detecção de loop/cancelamento (TASK-028/TASK-029/TASK-030).

Estados mínimos por ora: `PENDING`/`RUNNING`/`COMPLETED`/`FAILED` — o mesmo
conjunto usado pela fila (`docs/QUEUE.md`). Um estado `CANCELLED` pode ser
adicionado quando a TASK-030 (cancelamento) for implementada; não incluído
aqui para não adiantar essa TASK.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum

from app.llm.protocol import ModelStep


class ExecutionStatus(StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class InvalidExecutionStateError(RuntimeError):
    """Levantado ao tentar uma transição de estado inválida (ex.: adicionar
    etapa a uma execução que ainda não começou ou já terminou)."""


_TERMINAL_STATUSES = frozenset({ExecutionStatus.COMPLETED, ExecutionStatus.FAILED})


@dataclass
class Execution:
    """Uma execução em andamento no orquestrador."""

    execution_id: str
    origin: str
    status: ExecutionStatus = ExecutionStatus.PENDING
    steps: list[ModelStep] = field(default_factory=list)
    result: str | None = None
    error: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.execution_id or not self.execution_id.strip():
            raise ValueError("execution_id não pode ser vazio")
        if not self.origin or not self.origin.strip():
            raise ValueError("origin não pode ser vazio")

    def start(self) -> None:
        """`PENDING` → `RUNNING`."""
        if self.status != ExecutionStatus.PENDING:
            raise InvalidExecutionStateError(
                f"não é possível iniciar uma execução em estado {self.status}"
            )
        self.status = ExecutionStatus.RUNNING

    def add_step(self, step: ModelStep) -> None:
        """Registra uma etapa do protocolo (TASK-016). Só permitido com a
        execução `RUNNING`."""
        if self.status != ExecutionStatus.RUNNING:
            raise InvalidExecutionStateError(
                f"não é possível adicionar etapa a uma execução em estado {self.status}"
            )
        self.steps.append(step)

    def complete(self, result: str) -> None:
        """`RUNNING` → `COMPLETED`, registrando o resultado final."""
        if self.status != ExecutionStatus.RUNNING:
            raise InvalidExecutionStateError(
                f"não é possível concluir uma execução em estado {self.status}"
            )
        self.status = ExecutionStatus.COMPLETED
        self.result = result
        self.finished_at = datetime.now(timezone.utc)

    def fail(self, error: str) -> None:
        """Qualquer estado não-terminal → `FAILED`, registrando o erro."""
        if self.status in _TERMINAL_STATUSES:
            raise InvalidExecutionStateError(
                f"não é possível falhar uma execução em estado {self.status}"
            )
        self.status = ExecutionStatus.FAILED
        self.error = error
        self.finished_at = datetime.now(timezone.utc)

    @property
    def step_count(self) -> int:
        return len(self.steps)

    @property
    def is_terminal(self) -> bool:
        return self.status in _TERMINAL_STATUSES
