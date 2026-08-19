"""Rota de execuções da API local (TASK-067).

`POST /v1/executions`: ponto de entrada para uma aplicação externa pedir
uma execução ao Claudião (`docs/API.md`, seções 24/25/26). Esta TASK só
autentica a aplicação (`get_current_application`, TASK-067) e cria a
`Execution` (TASK-020) correspondente, devolvendo `execution_id`/`status`
— "cada requisição recebe um `execution_id` único" já é garantido por
`Execution.new()` (TASK-021).

Deliberadamente fora do escopo desta TASK: validar os campos do payload
além de ser um objeto JSON (TASK-068), executar de fato de forma síncrona
via `ExecutionOrchestrator` (TASK-069), aplicar/estourar timeout
(TASK-070/071), formato final de resposta de sucesso (TASK-072) e
rastreio de consumo (TASK-073). Por isso o corpo da requisição é aceito
como `dict` genérico, sem validação de schema, e a execução nunca sai de
`PENDING` aqui.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from app.api.auth import get_current_application
from app.auth.api_keys import Application
from app.orchestrator.execution import Execution

router = APIRouter()


@router.post("/v1/executions")
def create_execution(
    payload: dict[str, Any],
    application: Application = Depends(get_current_application),
) -> dict[str, str]:
    """Autentica a aplicação e cria uma execução nova. `payload` ainda não
    é validado (TASK-068) nem processado de fato (TASK-069)."""
    execution = Execution.new(origin=application.name)
    return {"execution_id": execution.execution_id, "status": execution.status.value}
