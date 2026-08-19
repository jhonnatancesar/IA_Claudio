"""Formato JSON padrão de sucesso da API local (TASK-072).

Espelha o formato padrão de erro (TASK-008, `app.errors.response`) —
`docs/ERROR_CATALOG.md`, "Formato padrão de resposta": toda resposta HTTP
da API tem um campo `success` (`bool`) no nível superior; em sucesso, o
payload específico da rota fica em `data`, à semelhança de como o erro
fica em `error`.
"""

from __future__ import annotations

from typing import Any


def build_success_response(data: dict[str, Any]) -> dict[str, Any]:
    """Monta o corpo JSON padrão de sucesso: `{"success": true, "data": data}`."""
    return {"success": True, "data": data}
