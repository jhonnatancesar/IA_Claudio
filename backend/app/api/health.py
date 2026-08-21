"""Rota de health check (TASK-085).

`GET /health`: expõe `app.observability.health_check.run_health_check`
sob demanda — para os eventos futuros que precisarem chamá-la de novo
(saída de manutenção/atualização/restore, TASK-123 em diante,
`docs/OPERATIONS.md`) e para verificação manual/operacional. Sem
autenticação, mesmo padrão do painel (`app.panel.routes`, TASK-081) —
health check é consultado por ferramentas de operação (load balancer,
script de deploy), não por uma aplicação autenticada; nenhuma
informação sensível é exposta (só nomes de checagem/status/mensagens de
erro genéricas).

HTTP `200` se `healthy`, `503` caso contrário — corpo igual nos dois
casos, para quem consome poder inspecionar exatamente o que falhou.
Não usa o envelope `{"success": bool, ...}` do resto da API
(`docs/ERROR_CATALOG.md`) — health check não é um erro de aplicação
sendo levantado, é uma consulta de estado; forçar isso no catálogo de
erros criaria um código sem sentido de negócio real.
"""

from __future__ import annotations

from fastapi import APIRouter, Response

from app.observability.health_check import run_health_check

router = APIRouter()


@router.get("/health")
def health(response: Response) -> dict:
    result = run_health_check()
    response.status_code = 200 if result.healthy else 503
    return {
        "healthy": result.healthy,
        "checks": [
            {"name": item.name, "status": item.status.value, "detail": item.detail}
            for item in result.items
        ],
    }
