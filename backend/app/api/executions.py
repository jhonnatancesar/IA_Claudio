"""Rota de execuções da API local (TASK-067, TASK-068, TASK-069).

`POST /v1/executions`: ponto de entrada para uma aplicação externa pedir
uma execução ao Claudião (`docs/API.md`, seções 24/25/26). Autentica a
aplicação (`get_current_application`, TASK-067), valida o payload contra
`ExecutionRequest` (TASK-068) e agora executa de fato, de forma
**síncrona**, via `ExecutionOrchestrator` (TASK-069, `run_until_response`)
— "a aplicação envia a requisição e espera o JSON final. Sem eventos
intermediários para a aplicação." "Cada requisição recebe um
`execution_id` único" continua garantido por `Execution.new()`
(TASK-021).

`ExecutionPolicy.for_application` (TASK-022) é montada a partir dos
campos já validados do payload (`timeout_seconds`/`web_search_allowed`/
`max_steps`) — `timeout_seconds` é aceito e guardado na política, mas
ainda não aplicado como limite de fato durante a execução (isso é
TASK-070); estourar e reportar esse limite formalmente é TASK-071.
Nenhum `tool_executor` é configurado ainda (Tool Registry é TASK-088 em
diante) — se o modelo pedir uma ferramenta,
`ToolExecutorNotConfiguredError` é convertida num erro claro em vez de
vazar como 500 não tratado. Falha de comunicação com o modelo local
(`LocalLLMProviderError`) é convertida do mesmo jeito. O formato final de
resposta de sucesso (envelope `"success": true`, à semelhança do
`"success": false` de erro) e rastreio de consumo são TASK-072/TASK-073,
não implementados aqui — a resposta de sucesso desta TASK é o mínimo
necessário (`execution_id`/`status`/`result`).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.auth import get_current_application
from app.api.dependencies import get_active_model, get_local_llm_provider
from app.api.schemas import ExecutionRequest
from app.auth.api_keys import Application
from app.errors.catalog import ErrorDomain, register_error
from app.errors.response import ClaudiaoError
from app.llm.provider import LocalLLMProvider, LocalLLMProviderError
from app.orchestrator.execution import Execution
from app.orchestrator.orchestrator import ExecutionOrchestrator, ToolExecutorNotConfiguredError
from app.policies.execution_policy import ExecutionPolicy

router = APIRouter()

MODEL_COMPLETION_FAILED = register_error(
    ErrorDomain.TOOLS_PROVIDERS, 3002, 502, "Falha ao completar com o modelo local"
)
TOOL_NOT_AVAILABLE = register_error(
    ErrorDomain.TOOLS_PROVIDERS,
    3003,
    501,
    "Ferramenta pedida pelo modelo ainda não está disponível",
)


@router.post("/v1/executions")
def create_execution(
    payload: ExecutionRequest,
    application: Application = Depends(get_current_application),
    provider: LocalLLMProvider = Depends(get_local_llm_provider),
    model: str = Depends(get_active_model),
) -> dict[str, str]:
    """Autentica, valida o payload e executa de fato, de forma síncrona,
    via `ExecutionOrchestrator` (TASK-069) — devolve o resultado final na
    mesma resposta HTTP, sem eventos intermediários."""
    policy_kwargs: dict = {
        "timeout_seconds": payload.timeout_seconds,
        "web_search_allowed": payload.web_search_allowed,
    }
    if payload.max_steps is not None:
        policy_kwargs["max_steps"] = payload.max_steps
    policy = ExecutionPolicy.for_application(**policy_kwargs)

    orchestrator = ExecutionOrchestrator(provider, policy)
    execution = Execution.new(origin=application.name)

    try:
        step = orchestrator.run_until_response(execution, payload.objective, model)
    except LocalLLMProviderError as exc:
        raise ClaudiaoError(MODEL_COMPLETION_FAILED, details={"reason": str(exc)}) from exc
    except ToolExecutorNotConfiguredError as exc:
        raise ClaudiaoError(TOOL_NOT_AVAILABLE, details={"reason": str(exc)}) from exc

    return {
        "execution_id": execution.execution_id,
        "status": execution.status.value,
        "result": step.reason,
    }
