"""Fila FIFO (TASK-074).

Seção 27 da especificação mestre (`docs/QUEUE.md`): "A V1 tem fila FIFO
persistida no PostgreSQL." Esta TASK cria só a fila em memória — ordem de
processamento (primeiro item enfileirado é o primeiro tirado) e o ciclo
de vida de cada item (`PENDING`/`RUNNING`/`COMPLETED`/`FAILED`, mesmo
conjunto documentado em `docs/QUEUE.md`), no mesmo espírito do modelo de
`Execution` (TASK-020): dataclass com transições de estado válidas,
sem depender de banco. Persistência real no PostgreSQL é TASK-075, não
implementada aqui.

Sem retry automático (seção 27): uma falha marca o item como `FAILED` e o
processamento segue para o próximo item da fila — não há reprocessamento
nem retomada de execução interrompida (fora da V1,
`docs/OUT_OF_SCOPE.md`).

`payload` é genérico (`Any`) de propósito — a fila não precisa saber o
que está enfileirando (execução, ferramenta, etc.); isso é decidido por
quem a usa, fora desta TASK (nenhuma TASK conecta a fila a
`POST /v1/executions`, que continua síncrono ponta a ponta).
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4


class QueueItemStatus(StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class InvalidQueueItemStateError(RuntimeError):
    """Levantado ao tentar uma transição de estado inválida (ex.:
    concluir um item que ainda não começou a rodar)."""


_TERMINAL_STATUSES = frozenset({QueueItemStatus.COMPLETED, QueueItemStatus.FAILED})


@dataclass
class QueueItem:
    """Um item da fila, do enfileiramento até a conclusão/falha."""

    item_id: str
    payload: Any
    status: QueueItemStatus = QueueItemStatus.PENDING
    error: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.item_id or not self.item_id.strip():
            raise ValueError("item_id não pode ser vazio")

    @classmethod
    def new(cls, payload: Any) -> "QueueItem":
        """Cria um `QueueItem` novo (`PENDING`), com `item_id` gerado
        automaticamente."""
        return cls(item_id=str(uuid4()), payload=payload)

    @property
    def is_terminal(self) -> bool:
        return self.status in _TERMINAL_STATUSES

    def start(self) -> None:
        """`PENDING` → `RUNNING`."""
        if self.status != QueueItemStatus.PENDING:
            raise InvalidQueueItemStateError(
                f"não é possível iniciar um item em estado {self.status}"
            )
        self.status = QueueItemStatus.RUNNING

    def complete(self) -> None:
        """`RUNNING` → `COMPLETED`."""
        if self.status != QueueItemStatus.RUNNING:
            raise InvalidQueueItemStateError(
                f"não é possível concluir um item em estado {self.status}"
            )
        self.status = QueueItemStatus.COMPLETED
        self.finished_at = datetime.now(timezone.utc)

    def fail(self, error: str) -> None:
        """Qualquer estado não-terminal → `FAILED`, registrando o erro.
        Sem retry automático (seção 27) — uma vez `FAILED`, o item não
        volta à fila."""
        if self.is_terminal:
            raise InvalidQueueItemStateError(
                f"não é possível falhar um item em estado {self.status}"
            )
        self.status = QueueItemStatus.FAILED
        self.error = error
        self.finished_at = datetime.now(timezone.utc)


class QueueEmptyError(RuntimeError):
    """Levantado ao tentar tirar um item de uma fila vazia."""


class FifoQueue:
    """Fila FIFO em memória: primeiro item enfileirado é o primeiro
    tirado (`dequeue`). Persistência real (TASK-075), estados adicionais
    (TASK-076) e retenção/limpeza (TASK-077) constroem em cima disto."""

    def __init__(self) -> None:
        self._items: deque[QueueItem] = deque()

    def enqueue(self, payload: Any) -> QueueItem:
        """Cria um `QueueItem` novo (`PENDING`) a partir de `payload` e o
        coloca no fim da fila."""
        item = QueueItem.new(payload)
        self._items.append(item)
        return item

    def dequeue(self) -> QueueItem:
        """Remove o item mais antigo da fila e o inicia (`start()` —
        `PENDING` → `RUNNING`), devolvendo-o para quem for processá-lo.
        Levanta `QueueEmptyError` se a fila estiver vazia."""
        if not self._items:
            raise QueueEmptyError("fila vazia")
        item = self._items.popleft()
        item.start()
        return item

    def __len__(self) -> int:
        return len(self._items)

    @property
    def is_empty(self) -> bool:
        return len(self._items) == 0
