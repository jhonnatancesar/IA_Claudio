"""Rota de execuções da API local (TASK-067, TASK-068).

`POST /v1/executions`: ponto de entrada para uma aplicação externa pedir
uma execução ao Claudião (`docs/API.md`, seções 24/25/26). Autentica a
aplicação (`get_current_application`, TASK-067), valida o payload contra
`ExecutionRequest` (TASK-068 — o próprio FastAPI rejeita automaticamente
um corpo incompleto ou com tipo errado, via o handler de
`RequestValidationError` em `app.py`) e cria a `Execution` (TASK-020)
correspondente, devolvendo `execution_id`/`status` — "cada requisição
recebe um `execution_id` único" já é garantido por `Execution.new()`
(TASK-021).

Deliberadamente fora do escopo desta TASK: montar a `ExecutionPolicy` de
fato a partir do payload e executar de verdade via
`ExecutionOrchestrator` (TASK-069), aplicar/estourar timeout
(TASK-070/071), formato final de resposta de sucesso (TASK-072) e
rastreio de consumo (TASK-073) — por isso os campos já validados do
payload ainda não são usados além de existir, e a execução nunca sai de
`PENDING` aqui.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.auth import get_current_application
from app.api.schemas import ExecutionRequest
from app.auth.api_keys import Application
from app.orchestrator.execution import Execution

router = APIRouter()


@router.post("/v1/executions")
def create_execution(
    payload: ExecutionRequest,
    application: Application = Depends(get_current_application),
) -> dict[str, str]:
    """Autentica a aplicação, valida o payload (`ExecutionRequest`,
    TASK-068) e cria uma execução nova. Os campos do payload ainda não são
    usados para processar de fato (TASK-069)."""
    execution = Execution.new(origin=application.name)
    return {"execution_id": execution.execution_id, "status": execution.status.value}
