"""Painel web read-only (TASK-081, TASK-082).

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
"""

from __future__ import annotations

from html import escape

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.observability.execution_trace import ExecutionTraceRecord, list_execution_traces
from app.queue.queue_model import QueueItem, list_queue_items

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


def render_panel_page(items: list[QueueItem], traces: list[ExecutionTraceRecord]) -> str:
    """Monta a página HTML completa do painel a partir dos itens da
    fila e dos traces de execução persistidos — separado de `panel_home`
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
        "</body>\n"
        "</html>\n"
    )


@router.get("/panel", response_class=HTMLResponse)
def panel_home() -> str:
    """Painel web read-only (TASK-081/082) — mostra o estado atual da
    fila e as execuções mais recentes."""
    return render_panel_page(list_queue_items(), list_execution_traces())
