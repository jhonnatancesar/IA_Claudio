"""Rota de execuções da API local (TASK-067 a TASK-071).

`POST /v1/executions`: ponto de entrada para uma aplicação externa pedir
uma execução ao Claudião (`docs/API.md`, seções 24/25/26). Autentica a
aplicação (`get_current_application`, TASK-067), valida o payload contra
`ExecutionRequest` (TASK-068) e executa de fato, de forma **síncrona**,
via `ExecutionOrchestrator` (TASK-069, `run_until_response`) — "a
aplicação envia a requisição e espera o JSON final. Sem eventos
intermediários para a aplicação." "Cada requisição recebe um
`execution_id` único" continua garantido por `Execution.new()`
(TASK-021).

`ExecutionPolicy.for_application` (TASK-022) é montada a partir dos
campos já validados do payload (`timeout_seconds`/`web_search_allowed`/
`max_steps`). Nenhum `tool_executor` é configurado ainda (Tool Registry é
TASK-088 em diante) — se o modelo pedir uma ferramenta,
`ToolExecutorNotConfiguredError` é convertida num erro claro em vez de
vazar como 500 não tratado. Falha de comunicação com o modelo local
(`LocalLLMProviderError`) é convertida do mesmo jeito. O formato final de
resposta de sucesso (envelope `"success": true`, à semelhança do
`"success": false` de erro) e rastreio de consumo são TASK-072/TASK-073,
não implementados aqui — a resposta de sucesso desta TASK é o mínimo
necessário (`execution_id`/`status`/`result`).

**Timeout (TASK-070):** `timeout_seconds` (do payload) é aplicado como
limite de verdade — "o timeout é definido pela própria aplicação... ao
estourar, o Claudião cancela a execução" (`docs/API.md`, seção 26).
`run_until_response` roda num worker de `_TIMEOUT_POOL`
(`ThreadPoolExecutor`); `future.result(timeout=...)` devolve o controle à
requisição HTTP assim que o prazo estoura, garantindo um limite de
verdade mesmo quando a chamada ao modelo em si está travada (uma única
etapa `RESPOND` não tem outro ponto de checagem cooperativa antes dela —
ver `app.orchestrator.cancellation`). Ao estourar, o `cancellation_token`
(TASK-030) compartilhado é cancelado — se o orquestrador estiver entre
etapas (fluxo com `USE_TOOL`), ele mesmo observa o cancelamento e chama
`execution.cancel(...)` em sua própria thread (única escritora de
`execution`, preservando "sem threads/async" do lado do orquestrador:
quem ganha uma thread aqui é só o limite HTTP, nunca o laço do
orquestrador em si); se a chamada travada terminar sozinha depois, ela
também cancela/completa `execution` normalmente, só que tarde demais para
influenciar a resposta HTTP já enviada — limitação inerente a cancelamento
cooperativo e não-preemptivo, aceita conscientemente aqui.

**Erro de timeout (TASK-071):** `APPLICATION_TIMEOUT_EXCEEDED` (código
4009, HTTP 504) — os `details` trazem `timeout_seconds` (TASK-070) mais
"etapa atual e ferramenta ativa" (`docs/API.md`, seção 26):
`current_step` é `execution.step_count + 1` (a etapa que estava em
andamento quando o prazo estourou, 1-indexada) e `active_tool` é o `tool`
da última etapa já registrada em `execution.steps` (`None` se nenhuma
etapa foi registrada ainda, ou se a última foi `RESPOND`). Como nenhum
`tool_executor` está configurado ainda (Tool Registry, TASK-088+), na
prática hoje `execution.steps` costuma estar vazia no momento do timeout
(a única etapa em andamento é a primeira chamada ao modelo, ainda não
registrada) — o valor cresce em utilidade conforme fluxos com `USE_TOOL`
passarem a existir de verdade.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError

from fastapi import APIRouter, Depends

from app.api.auth import get_current_application
from app.api.dependencies import get_active_model, get_local_llm_provider
from app.api.schemas import ExecutionRequest
from app.auth.api_keys import Application
from app.errors.catalog import ErrorDomain, register_error
from app.errors.response import ClaudiaoError
from app.llm.provider import LocalLLMProvider, LocalLLMProviderError
from app.orchestrator.cancellation import CancellationToken
from app.orchestrator.execution import Execution
from app.orchestrator.orchestrator import ExecutionOrchestrator, ToolExecutorNotConfiguredError
from app.policies.execution_policy import ExecutionPolicy

router = APIRouter()

_TIMEOUT_POOL = ThreadPoolExecutor(max_workers=8, thread_name_prefix="claudiao-execution")
_TIMEOUT_REASON = "timeout da aplicação"

MODEL_COMPLETION_FAILED = register_error(
    ErrorDomain.TOOLS_PROVIDERS, 3002, 502, "Falha ao completar com o modelo local"
)
TOOL_NOT_AVAILABLE = register_error(
    ErrorDomain.TOOLS_PROVIDERS,
    3003,
    501,
    "Ferramenta pedida pelo modelo ainda não está disponível",
)
APPLICATION_TIMEOUT_EXCEEDED = register_error(
    ErrorDomain.MODEL_ORCHESTRATOR,
    4009,
    504,
    "Execução cancelada por timeout da aplicação",
)


def _timeout_error_details(execution: Execution, timeout_seconds: float) -> dict:
    """Monta os `details` de `APPLICATION_TIMEOUT_EXCEEDED` (TASK-071) —
    "etapa atual e ferramenta ativa" (`docs/API.md`, seção 26). `execution`
    é lida no exato momento do timeout, sem sincronização com a thread do
    orquestrador (ver docstring do módulo) — melhor esforço, não garantia
    atômica.

    `current_step` (1-indexado) é a etapa que estava em andamento quando o
    prazo estourou: `execution.step_count` etapas já foram registradas, a
    próxima (`+ 1`) é a que travou. `active_tool` é o `tool` da última
    etapa já registrada, ou `None` se nenhuma etapa foi registrada ainda
    (comum hoje, já que nenhum `tool_executor` está configurado) ou se a
    última etapa não usava ferramenta.
    """
    last_step = execution.steps[-1] if execution.steps else None
    return {
        "timeout_seconds": timeout_seconds,
        "current_step": execution.step_count + 1,
        "active_tool": last_step.tool if last_step is not None else None,
    }


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
    cancellation_token = CancellationToken()

    future = _TIMEOUT_POOL.submit(
        orchestrator.run_until_response,
        execution,
        payload.objective,
        model,
        cancellation_token,
    )
    try:
        step = future.result(timeout=payload.timeout_seconds)
    except FutureTimeoutError:
        cancellation_token.cancel(reason=_TIMEOUT_REASON)
        raise ClaudiaoError(
            APPLICATION_TIMEOUT_EXCEEDED,
            details=_timeout_error_details(execution, payload.timeout_seconds),
        ) from None
    except LocalLLMProviderError as exc:
        raise ClaudiaoError(MODEL_COMPLETION_FAILED, details={"reason": str(exc)}) from exc
    except ToolExecutorNotConfiguredError as exc:
        raise ClaudiaoError(TOOL_NOT_AVAILABLE, details={"reason": str(exc)}) from exc

    return {
        "execution_id": execution.execution_id,
        "status": execution.status.value,
        "result": step.reason,
    }
