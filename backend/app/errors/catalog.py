"""Catálogo interno de erros do Claudião (TASK-007).

Registra os códigos internos de erro por faixa (docs/ERROR_CATALOG.md, seção 36 da
especificação mestre). Só o catálogo — o formato de resposta JSON padrão que usa
esses códigos (`{"success": false, "error": {...}}`) é escopo da TASK-008, não
implementado aqui.

O catálogo nasce pequeno, de propósito: só os erros que a própria fundação já
precisa (validação genérica, erro interno genérico). Cada TASK futura que precisar
de um código novo o registra aqui via `register_error()` quando chegar sua vez —
não adiantamos códigos de módulos que ainda não existem.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class ErrorDomain(IntEnum):
    """Faixas de código por domínio, largura 1000 cada (docs/ERROR_CATALOG.md)."""

    VALIDATION = 1000
    AUTH = 2000
    TOOLS_PROVIDERS = 3000
    MODEL_ORCHESTRATOR = 4000
    MEMORY_KNOWLEDGE = 5000
    DATABASE = 6000
    QUOTAS_PROCESSING = 7000
    INTEGRATIONS_APPLICATIONS = 8000
    INTERNAL_GENERIC = 9000


_DOMAIN_WIDTH = 1000


@dataclass(frozen=True)
class ErrorDefinition:
    """Um erro conhecido do catálogo: código interno, HTTP padrão e mensagem."""

    code: int
    http_status: int
    message: str


class DuplicateErrorCodeError(ValueError):
    """Levantado ao tentar registrar um código já usado por outra definição."""


class ErrorCodeOutOfRangeError(ValueError):
    """Levantado quando o código não cai na faixa do domínio informado."""


_REGISTRY: dict[int, ErrorDefinition] = {}


def domain_for_code(code: int) -> ErrorDomain:
    """Resolve a que domínio um código pertence, pela faixa em que ele cai."""
    base = (code // _DOMAIN_WIDTH) * _DOMAIN_WIDTH
    try:
        return ErrorDomain(base)
    except ValueError as exc:
        raise ErrorCodeOutOfRangeError(
            f"código {code} não pertence a nenhuma faixa de domínio conhecida"
        ) from exc


def register_error(
    domain: ErrorDomain, code: int, http_status: int, message: str
) -> ErrorDefinition:
    """Registra uma nova definição de erro no catálogo.

    Levanta `ErrorCodeOutOfRangeError` se `code` não pertencer à faixa de `domain`,
    e `DuplicateErrorCodeError` se `code` já estiver registrado.
    """
    if not (domain.value <= code < domain.value + _DOMAIN_WIDTH):
        raise ErrorCodeOutOfRangeError(
            f"código {code} está fora da faixa do domínio {domain.name} "
            f"({domain.value}-{domain.value + _DOMAIN_WIDTH - 1})"
        )
    if code in _REGISTRY:
        existing = _REGISTRY[code]
        raise DuplicateErrorCodeError(
            f"código {code} já registrado como {existing.message!r}"
        )
    definition = ErrorDefinition(code=code, http_status=http_status, message=message)
    _REGISTRY[code] = definition
    return definition


def get_error(code: int) -> ErrorDefinition:
    """Busca uma definição de erro registrada. Levanta `KeyError` se não existir."""
    return _REGISTRY[code]


def all_errors() -> dict[int, ErrorDefinition]:
    """Retorna uma cópia somente-leitura do catálogo registrado até agora."""
    return dict(_REGISTRY)


# --- Erros seed da fundação (docs/ERROR_CATALOG.md; seção 36 da especificação) ---

MISSING_REQUIRED_FIELD = register_error(
    ErrorDomain.VALIDATION, 1001, 400, "Campo obrigatório ausente"
)
INVALID_FIELD_VALUE = register_error(
    ErrorDomain.VALIDATION, 1002, 400, "Valor de campo inválido"
)
UNKNOWN_INTERNAL_ERROR = register_error(
    ErrorDomain.INTERNAL_GENERIC, 9000, 500, "Erro interno desconhecido"
)
