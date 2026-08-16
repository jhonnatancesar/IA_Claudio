"""Papéis ADMIN e USER (TASK-010).

Autorização por papel: o que cada papel pode fazer (docs/AUTHENTICATION.md,
seção 31 da especificação — USER tem chat/histórico/memória próprios, sem
painel administrativo; ADMIN tem gestão completa). Autenticação (quem é o
usuário) é escopo da TASK-009 (`app.auth.users`) — este módulo opera sobre o
`role` (string), não sobre a classe `User`, para não criar dependência
circular entre os dois módulos.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from app.errors.catalog import ErrorDomain, register_error
from app.errors.response import ClaudiaoError


class Role(StrEnum):
    ADMIN = "ADMIN"
    USER = "USER"


FORBIDDEN_ADMIN_ONLY = register_error(
    ErrorDomain.AUTH, 2001, 403, "Ação restrita a administradores"
)


def is_admin(role: str) -> bool:
    """`True` se `role` for `ADMIN`. Qualquer valor que não seja `Role.ADMIN`
    (incluindo papéis desconhecidos) é tratado como não-admin."""
    return role == Role.ADMIN.value


def require_admin(role: str, *, details: dict[str, Any] | None = None) -> None:
    """Levanta `ClaudiaoError` (403, `FORBIDDEN_ADMIN_ONLY`) se `role` não for
    `ADMIN`. Quem chama decide o que colocar em `details` (ex.: username)."""
    if not is_admin(role):
        raise ClaudiaoError(FORBIDDEN_ADMIN_ONLY, details=details)
