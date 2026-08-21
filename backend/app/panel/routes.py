"""Painel web read-only (TASK-081, TASK-082, TASK-083).

"Painel inicial (somente leitura)" (`docs/PANEL.md`, seções 37/38): antes
do painel administrativo completo (TASK-115 em diante), existe uma
superfície web somente leitura para acompanhar aplicações e execuções —
fila, execução atual, status, logs recentes, erros, consumo básico,
resultados das execuções.

Esta TASK cria a base (router FastAPI, incluído no mesmo `app`
de `app.api.app` — não há decisão de rodar o painel num processo/porta
separados) e mostra o primeiro item da lista que já tem dado real e
persistido: a fila (`app.queue.queue_model.list_queue_items`,
TASK-075). "Logs/erros/consumo" (TASK-083) mostram o resto depois.

Sem autenticação por ora: `docs/PANEL.md` descreve regras de acesso
(confirmação, senha do `ADMIN`, logout por inatividade) só na seção do
painel **administrativo completo** (TASK-115+), não na seção do painel
inicial somente leitura acima dela. Nenhuma TASK anterior construiu uma
sessão de usuário via navegador (autenticação por API key, TASK-011, é
para aplicações, não humanos clicando numa página) — exigir login aqui
seria inventar um mecanismo de sessão não pedido por esta TASK. Página
somente leitura (só rotas `GET`), sem exibir nada além do que a fila já
guarda (`item_id`/`status`/`created_at`/`finished_at` — nunca
`payload`, que pode conter dado arbitrário de quem enfileirou).

Esta TASK (TASK-082) acrescenta "Execuções": `app.observability.
execution_trace.list_execution_traces` (persistência decidida nesta
mesma TASK, `DEC-010`, `docs/DECISION_LOG.md`, já que a especificação
mestre não exige isso para o Execution Trace) — `execution_id`/
`requester`/`objective`/status (derivado de `succeeded`)/`result`/
`duration_seconds`. `objective`/`result` são texto livre (vêm da
aplicação chamadora/do modelo) — escapados via `html.escape` antes de
entrar na página, diferente dos campos da fila (todos gerados pelo
próprio sistema, sem risco de injeção).

Esta TASK (TASK-083) acrescenta as três seções finais do painel inicial
somente leitura (`docs/PANEL.md`): "Logs recentes"
(`app.observability.postgres_log_handler.list_recent_logs` — na prática
hoje costuma vir vazia, já que nenhum módulo da aplicação chama
`logger.error`/`logger.warning` em nenhum ponto real ainda, lacuna
conhecida documentada em `postgres_log_handler.py`); "Erros"
(`app.observability.execution_trace.list_failed_execution_traces` —
execuções persistidas com `result IS NULL`, o único sinal de erro com
dado real hoje); "Consumo" (`app.usage.usage_model.
list_recent_usage_records` — requisições reais de qualquer aplicação,
já persistidas desde a TASK-073). Com esta TASK, o bloco
"Observabilidade inicial" (TASK-078 a TASK-083) está completo.
"""

from __future__ import annotations

from html import escape

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.observability.execution_trace import (
    ExecutionTraceRecord,
    list_execution_traces,
    list_failed_execution_traces,
)
from app.observability.postgres_log_handler import LogEntry, list_recent_logs
from app.queue.queue_model import QueueItem, list_queue_items
from app.usage.usage_model import UsageRecord, list_recent_usage_records

router = APIRouter()


def _render_queue_table(items: list[QueueItem]) -> str:
    if not items:
        return "<p>Fila vazia.</p>"
    rows = "\n".join(
        "<tr><td>{id}</td><td>{status}</td><td>{created_at}</td><td>{finished_at}</td></tr>".format(
            id=item.item_id,
            status=item.status.value,
            created_at=item.created_at.isoformat(),
            finished_at=item.finished_at.isoformat() if item.finished_at else "",
        )
        for item in items
    )
    return (
        "<table>\n"
        "<thead><tr><th>ID</th><th>Status</th><th>Criado em</th><th>Terminado em</th></tr></thead>\n"
        f"<tbody>\n{rows}\n</tbody>\n"
        "</table>"
    )


def _render_executions_table(traces: list[ExecutionTraceRecord]) -> str:
    if not traces:
        return "<p>Nenhuma execução registrada ainda.</p>"
    rows = "\n".join(
        "<tr><td>{id}</td><td>{requester}</td><td>{objective}</td><td>{status}</td>"
        "<td>{result}</td><td>{duration}</td></tr>".format(
            id=escape(trace.execution_id),
            requester=escape(trace.requester),
            objective=escape(trace.objective),
            status="sucesso" if trace.succeeded else "falha",
            result=escape(trace.result) if trace.result is not None else "",
            duration=(
                f"{trace.duration_seconds:.2f}s" if trace.duration_seconds is not None else ""
            ),
        )
        for trace in traces
    )
    return (
        "<table>\n"
        "<thead><tr><th>ID</th><th>Aplicação</th><th>Objetivo</th><th>Status</th>"
        "<th>Resultado</th><th>Duração</th></tr></thead>\n"
        f"<tbody>\n{rows}\n</tbody>\n"
        "</table>"
    )


def _render_logs_table(logs: list[LogEntry]) -> str:
    if not logs:
        return "<p>Nenhum log registrado ainda.</p>"
    rows = "\n".join(
        "<tr><td>{timestamp}</td><td>{level}</td><td>{logger}</td><td>{message}</td></tr>".format(
            timestamp=log.timestamp.isoformat(),
            level=escape(log.level),
            logger=escape(log.logger),
            message=escape(log.message),
        )
        for log in logs
    )
    return (
        "<table>\n"
        "<thead><tr><th>Quando</th><th>Nível</th><th>Logger</th><th>Mensagem</th></tr></thead>\n"
        f"<tbody>\n{rows}\n</tbody>\n"
        "</table>"
    )


def _render_errors_table(traces: list[ExecutionTraceRecord]) -> str:
    if not traces:
        return "<p>Nenhum erro registrado ainda.</p>"
    rows = "\n".join(
        "<tr><td>{id}</td><td>{requester}</td><td>{objective}</td><td>{finished_at}</td></tr>".format(
            id=escape(trace.execution_id),
            requester=escape(trace.requester),
            objective=escape(trace.objective),
            finished_at=trace.finished_at.isoformat() if trace.finished_at else "",
        )
        for trace in traces
    )
    return (
        "<table>\n"
        "<thead><tr><th>ID</th><th>Aplicação</th><th>Objetivo</th><th>Terminado em</th></tr></thead>\n"
        f"<tbody>\n{rows}\n</tbody>\n"
        "</table>"
    )


def _render_usage_table(records: list[UsageRecord]) -> str:
    if not records:
        return "<p>Nenhum consumo registrado ainda.</p>"
    rows = "\n".join(
        "<tr><td>{execution_id}</td><td>{application_id}</td><td>{status}</td>"
        "<td>{created_at}</td></tr>".format(
            execution_id=escape(record.execution_id),
            application_id=str(record.application_id),
            status=escape(record.status),
            created_at=record.created_at.isoformat(),
        )
        for record in records
    )
    return (
        "<table>\n"
        "<thead><tr><th>Execução</th><th>Aplicação</th><th>Status</th><th>Quando</th></tr></thead>\n"
        f"<tbody>\n{rows}\n</tbody>\n"
        "</table>"
    )


def render_panel_page(
    items: list[QueueItem],
    traces: list[ExecutionTraceRecord],
    logs: list[LogEntry],
    failed_traces: list[ExecutionTraceRecord],
    usage_records: list[UsageRecord],
) -> str:
    """Monta a página HTML completa do painel — separado de `panel_home`
    para ser testável sem passar pelo FastAPI."""
    return (
        "<!doctype html>\n"
        '<html lang="pt-BR">\n'
        "<head>\n"
        '<meta charset="utf-8">\n'
        "<title>Claudião — Painel</title>\n"
        "</head>\n"
        "<body>\n"
        "<h1>Claudião — Painel (somente leitura)</h1>\n"
        "<h2>Fila</h2>\n"
        f"{_render_queue_table(items)}\n"
        "<h2>Execuções</h2>\n"
        f"{_render_executions_table(traces)}\n"
        "<h2>Erros</h2>\n"
        f"{_render_errors_table(failed_traces)}\n"
        "<h2>Logs recentes</h2>\n"
        f"{_render_logs_table(logs)}\n"
        "<h2>Consumo</h2>\n"
        f"{_render_usage_table(usage_records)}\n"
        "</body>\n"
        "</html>\n"
    )


@router.get("/panel", response_class=HTMLResponse)
def panel_home() -> str:
    """Painel web read-only (TASK-081 a TASK-083) — mostra o estado
    atual da fila, as execuções mais recentes, erros, logs recentes e
    consumo básico."""
    return render_panel_page(
        list_queue_items(),
        list_execution_traces(),
        list_recent_logs(),
        list_failed_execution_traces(),
        list_recent_usage_records(),
    )
