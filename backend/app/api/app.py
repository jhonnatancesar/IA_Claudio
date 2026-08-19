"""API local do Claudião (TASK-067).

Camada de entrada HTTP para aplicações externas (`docs/API.md`, seções
24/25/26) — FastAPI escolhido pelo usuário nesta TASK (framework web
estava em aberto, `docs/OPEN_QUESTIONS.md`, item 1; ver
`docs/DECISION_LOG.md`, DEC-009). "A comunicação com aplicações usa
JSON" — qualquer `ClaudiaoError` levantada por uma rota (ex.:
`get_current_application`, TASK-067) é convertida para o formato JSON
padrão de erro do projeto (`app.errors.response`, TASK-008) pelo handler
abaixo, em vez do formato default do FastAPI (`{"detail": ...}`).

Validação de payload (TASK-068), execução síncrona de fato (TASK-069),
timeout (TASK-070/071), formato de resposta de sucesso (TASK-072) e
rastreio de consumo (TASK-073) não são desta TASK.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.executions import router as executions_router
from app.errors.response import ClaudiaoError, error_response_from_exception

app = FastAPI(title="Claudião API")
app.include_router(executions_router)


@app.exception_handler(ClaudiaoError)
async def _handle_claudiao_error(request: Request, exc: ClaudiaoError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.definition.http_status,
        content=error_response_from_exception(exc),
    )
