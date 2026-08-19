"""Desbloqueio somente ADMIN (TASK-066).

`unblock_source` (TASK-064) é mecânico — não checa quem está autorizado a
chamar, só que a fonte esteja de fato bloqueada. Esta TASK acrescenta essa
checagem: "o `ADMIN` pode bloquear e desbloquear manualmente. **Se o
agente bloquear, ele não pode desbloquear sozinho** — somente o `ADMIN`"
(`docs/TRUST_GUARDRAILS.md`, seção 14/15). A leitura mais direta é que
desbloquear exige papel `ADMIN` sempre, não só quando foi o agente que
bloqueou — nada no sistema permite ao agente desbloquear em nenhuma
circunstância.

`admin_unblock_source` reaproveita `app.auth.roles.require_admin`
(TASK-010) em vez de duplicar lógica de autorização — a mesma checagem
(e o mesmo código de erro, `FORBIDDEN_ADMIN_ONLY`, 2001) já usada em
qualquer outra ação restrita a `ADMIN` no projeto.
"""

from __future__ import annotations

from uuid import UUID

from app.auth.roles import require_admin
from app.sources.source_registry import BlockOrigin, Source, unblock_source


def admin_unblock_source(
    source_id: UUID, role: str, responsible: str, reason: str
) -> Source:
    """Desbloqueia uma fonte, só se `role` for `ADMIN`
    (`require_admin` — levanta `ClaudiaoError(FORBIDDEN_ADMIN_ONLY)` antes
    de tocar qualquer estado, se não for). `responsible` identifica o
    `ADMIN` responsável; levanta `ValueError` se vazio. Repassa
    `SourceNotFoundError`/`SourceBlacklistStateError` de `unblock_source`
    (TASK-064) inalterados."""
    require_admin(role, details={"responsible": responsible})
    if not responsible or not responsible.strip():
        raise ValueError("responsible não pode ser vazio")

    return unblock_source(source_id, BlockOrigin.ADMIN, reason, responsible=responsible)
