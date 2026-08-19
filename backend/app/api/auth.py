"""Autenticação de aplicações na API HTTP (TASK-067).

Reaproveita `app.auth.api_keys.authenticate_application` (TASK-011) — não
reimplementa verificação de API key, só extrai a key do header
`Authorization: Bearer <api_key>` (convenção HTTP padrão) e expõe a
`Application` autenticada como dependência do FastAPI para as rotas.
`ClaudiaoError` (TASK-008) é levantada em vez de `HTTPException` para que
a resposta de erro siga o mesmo formato JSON padrão do resto do
projeto — o handler global em `app.api.app` converte qualquer
`ClaudiaoError` para essa resposta.
"""

from __future__ import annotations

from fastapi import Header

from app.auth.api_keys import Application, authenticate_application
from app.errors.catalog import ErrorDomain, register_error
from app.errors.response import ClaudiaoError

INVALID_API_KEY = register_error(
    ErrorDomain.AUTH, 2002, 401, "API key ausente ou inválida"
)


def _extract_bearer_token(authorization: str | None) -> str | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    return authorization.removeprefix("Bearer ")


def get_current_application(authorization: str | None = Header(default=None)) -> Application:
    """Dependência do FastAPI: autentica a aplicação chamadora pelo header
    `Authorization: Bearer <api_key>`. Levanta `ClaudiaoError`
    (`INVALID_API_KEY`, 401) se o header estiver ausente, malformado, ou a
    key não corresponder a nenhuma aplicação cadastrada."""
    api_key = _extract_bearer_token(authorization)
    application = authenticate_application(api_key) if api_key else None
    if application is None:
        raise ClaudiaoError(INVALID_API_KEY)
    return application
