"""Formato de resposta JSON padrão de erro do Claudião (TASK-008).

Usa o catálogo de erros da TASK-007 (`app.errors.catalog`). Formato fixo pela
especificação mestre, seção 36:

```json
{
  "success": false,
  "error": {
    "http_status": 400,
    "code": 1001,
    "message": "Campo obrigatório ausente",
    "details": {"field": "query"}
  }
}
```

Só o formato de erro — resposta de sucesso é escopo de outra TASK (TASK-072,
resposta JSON final da API), não implementada aqui.
"""

from __future__ import annotations

from typing import Any

from app.errors.catalog import ErrorDefinition


class ClaudiaoError(Exception):
    """Exceção que carrega uma definição do catálogo de erros, com detalhes
    opcionais específicos da ocorrência (ex.: qual campo faltou)."""

    def __init__(
        self, definition: ErrorDefinition, details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(f"[{definition.code}] {definition.message}")
        self.definition = definition
        self.details = details


def build_error_response(
    definition: ErrorDefinition, details: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Monta o corpo JSON padrão de erro (seção 36 da especificação mestre).

    `details` só aparece na resposta quando fornecido e não vazio.
    """
    error: dict[str, Any] = {
        "http_status": definition.http_status,
        "code": definition.code,
        "message": definition.message,
    }
    if details:
        error["details"] = details
    return {"success": False, "error": error}


def error_response_from_exception(exc: ClaudiaoError) -> dict[str, Any]:
    """Atalho: monta a resposta padrão a partir de uma `ClaudiaoError` levantada."""
    return build_error_response(exc.definition, exc.details)
