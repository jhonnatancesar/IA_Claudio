"""Painel web read-only (TASK-081).

"Painel inicial (somente leitura)" (`docs/PANEL.md`, seções 37/38): antes
do painel administrativo completo (TASK-115 em diante), existe uma
superfície web somente leitura para acompanhar aplicações e execuções —
fila, execução atual, status, logs recentes, erros, consumo básico,
resultados das execuções.

Esta TASK cria a base (router FastAPI, incluído no mesmo `app`
de `app.api.app` — não há decisão de rodar o painel num processo/porta
separados) e mostra o primeiro item da lista que já tem dado real e
persistido hoje: a fila (`app.queue.queue_model.list_queue_items`,
TASK-075). "Execução atual"/"resultados das execuções" (TASK-082) e
"logs/erros/consumo" (TASK-083) mostram o resto depois —
`ExecutionTrace` (TASK-078/079) não é persistido em lugar nenhum ainda,
então essas duas provavelmente vão exigir uma decisão de arquitetura
nova (onde guardar traces) fora do escopo desta TASK.

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
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

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


def render_panel_page(items: list[QueueItem]) -> str:
    """Monta a página HTML completa do painel a partir dos itens da
    fila — separado de `panel_home` para ser testável sem passar pelo
    FastAPI."""
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
        "</body>\n"
        "</html>\n"
    )


@router.get("/panel", response_class=HTMLResponse)
def panel_home() -> str:
    """Painel web read-only (TASK-081) — mostra o estado atual da fila."""
    return render_panel_page(list_queue_items())
