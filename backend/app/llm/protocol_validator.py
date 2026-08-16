"""Validação dos JSONs internos do protocolo modelo↔orquestrador (TASK-017).

Constrói em cima do parser estrutural da TASK-016 (`app.llm.protocol.ModelStep`
— campos obrigatórios, valores dentro do enum): adiciona validação semântica
mais estrita (`execution_id` precisa ter formato de UUID, `reason` não pode
ser vazio) e traduz qualquer falha do protocolo para o catálogo de erros
formal (TASK-007/TASK-008), faixa `MODEL_ORCHESTRATOR` (4000-4999) — para que
o orquestrador (ainda não implementado, TASK-020 em diante) trate isso como
qualquer outro erro da aplicação, com HTTP/código/mensagem padronizados.
"""

from __future__ import annotations

from uuid import UUID

from app.errors.catalog import ErrorDomain, register_error
from app.errors.response import ClaudiaoError
from app.llm.protocol import ModelStep, ProtocolDecodeError

INVALID_MODEL_STEP = register_error(
    ErrorDomain.MODEL_ORCHESTRATOR, 4001, 502,
    "JSON do modelo fora do protocolo esperado",
)


def _validate_semantics(step: ModelStep) -> None:
    """Checagens semânticas que o parser estrutural da TASK-016 não faz."""
    try:
        UUID(step.execution_id)
    except (ValueError, AttributeError, TypeError) as exc:
        raise ProtocolDecodeError(
            f"execution_id não é um UUID válido: {step.execution_id!r}"
        ) from exc

    if not step.reason.strip():
        raise ProtocolDecodeError("reason não pode ser vazio")


def validate_step(raw: str) -> ModelStep:
    """Decodifica e valida um JSON de etapa vindo do modelo.

    Levanta `ClaudiaoError` (`INVALID_MODEL_STEP`, código 4001) para qualquer
    falha — JSON malformado, campo obrigatório ausente, valor fora do enum, ou
    uma das checagens semânticas adicionais desta TASK. O motivo específico
    fica em `details["reason"]`.
    """
    try:
        step = ModelStep.from_json(raw)
        _validate_semantics(step)
    except ProtocolDecodeError as exc:
        raise ClaudiaoError(
            INVALID_MODEL_STEP, details={"reason": str(exc)}
        ) from exc
    return step
