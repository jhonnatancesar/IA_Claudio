"""API local do Claudião (TASK-067, TASK-068, TASK-081).

Camada de entrada HTTP para aplicações externas (`docs/API.md`, seções
24/25/26) — FastAPI escolhido pelo usuário nesta TASK (framework web
estava em aberto, `docs/OPEN_QUESTIONS.md`, item 1; ver
`docs/DECISION_LOG.md`, DEC-009). "A comunicação com aplicações usa
JSON" — qualquer `ClaudiaoError` levantada por uma rota (ex.:
`get_current_application`, TASK-067) é convertida para o formato JSON
padrão de erro do projeto (`app.errors.response`, TASK-008) pelo handler
abaixo, em vez do formato default do FastAPI (`{"detail": ...}`).

TASK-068 acrescenta o mesmo tratamento para `RequestValidationError` — o
erro que o FastAPI levanta quando o corpo da requisição não bate com
`ExecutionRequest` (`app.api.schemas`, campo obrigatório ausente ou
tipo/valor errado): "se faltar campo obrigatório, retorna erro
imediatamente, sem inferir ou preencher" (`docs/API.md`). Reaproveita os
códigos de erro genéricos já existentes desde a fundação
(`MISSING_REQUIRED_FIELD`, 1001; `INVALID_FIELD_VALUE`, 1002 — TASK-007),
em vez de criar códigos novos só para isto.

Montar a `ExecutionPolicy` de fato e executar via `ExecutionOrchestrator`
(TASK-069), timeout (TASK-070/071), formato de resposta de sucesso
(TASK-072) e rastreio de consumo (TASK-073) não são desta TASK.

TASK-081 acrescenta o painel web read-only (`app.panel.routes`) no mesmo
`app` — sem decisão de rodar API de aplicações e painel humano em
processos/portas separados, V1 mínima.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.executions import router as executions_router
from app.errors.catalog import INVALID_FIELD_VALUE, MISSING_REQUIRED_FIELD
from app.errors.response import ClaudiaoError, build_error_response, error_response_from_exception
from app.panel.routes import router as panel_router

app = FastAPI(title="Claudião API")
app.include_router(executions_router)
app.include_router(panel_router)


@app.exception_handler(ClaudiaoError)
async def _handle_claudiao_error(request: Request, exc: ClaudiaoError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.definition.http_status,
        content=error_response_from_exception(exc),
    )


@app.exception_handler(RequestValidationError)
async def _handle_validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = exc.errors()
    definition = (
        MISSING_REQUIRED_FIELD
        if errors and errors[0]["type"] == "missing"
        else INVALID_FIELD_VALUE
    )
    details = {
        "errors": [
            {"field": ".".join(str(part) for part in error["loc"]), "message": error["msg"]}
            for error in errors
        ]
    }
    return JSONResponse(
        status_code=definition.http_status,
        content=build_error_response(definition, details),
    )
