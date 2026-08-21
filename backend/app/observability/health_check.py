"""Health check inicial (TASK-085).

Seções 39/40/41 da especificação mestre (`docs/OPERATIONS.md`, "Health
check"): "Na V1, roda apenas em eventos importantes: inicialização,
saída de manutenção, atualização e restore/rollback. Verifica:
modelo/runtime, PostgreSQL, fila, ferramentas/providers principais,
configurações críticas. Sem health check periódico em background na V1."

Desta lista de eventos, só **inicialização** é alcançável hoje — saída
de manutenção, atualização e restore/rollback são TASK-123 em diante,
ainda não implementados. `run_health_check()` é chamada no evento de
inicialização (`app.api.app`, evento `startup` do FastAPI) e também
exposta sob demanda (`GET /health`, `app.api.health`) para quando as
outras TASKs (123+) precisarem chamá-la de novo nos próprios eventos —
"sem periódico em background" continua respeitado: só roda quando
alguém chama, nunca sozinha num laço.

Cada item verificado, mapeado para a lista da especificação:

- `modelo/runtime` — `OllamaProvider().is_available()` (TASK-015), a
  mesma checagem leve já usada para health checks futuros
  (`docs/ARCHITECTURE.md`).
- `postgresql` — abre uma conexão de verdade e roda `SELECT 1`
  (`app.db.connection.connect`).
- `fila` — `app.queue.queue_model.list_queue_items()` não levanta
  (TASK-075) — confirma que a tabela existe e é consultável, indo além
  do check genérico de `postgresql` (pega, por exemplo, uma migration
  não aplicada).
- `ferramentas/providers principais` — **`SKIPPED`**, não `FAILED`:
  nenhuma ferramenta existe ainda (Tool Registry é TASK-088 em diante),
  não há o que checar — vacuamente "sem problema", não "verificado e
  funcionando".
- `configurações críticas` — `CLAUDIAO_ACTIVE_MODEL` definida e a chave
  mestra (`app.auth.master_key.load_or_create_master_key`, TASK-013)
  carregável (cria se ainda não existir — mesmo comportamento de
  primeira inicialização já garantido pela TASK-013, só exercitado
  aqui).

Cada item com `FAILED` é registrado via `logger.error` (`app.observability.
logging_config`, TASK-005/006) — primeira conexão real de código de
aplicação ao logging estruturado; até aqui, nada chamava
`logger.error`/`logger.warning` em nenhum ponto do fluxo real (lacuna
registrada na TASK-083, `docs/OBSERVABILITY.md`). Um resumo (`INFO` se
saudável, `WARNING` caso contrário) também é registrado.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import StrEnum

from app.auth.master_key import MasterKeyPathNotConfiguredError, load_or_create_master_key
from app.db.connection import connect
from app.llm.providers.ollama_provider import OllamaProvider
from app.observability.logging_config import get_logger
from app.queue.queue_model import list_queue_items

_logger = get_logger("health_check")


class HealthCheckStatus(StrEnum):
    OK = "OK"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


@dataclass(frozen=True)
class HealthCheckItem:
    name: str
    status: HealthCheckStatus
    detail: str | None = None


@dataclass(frozen=True)
class HealthCheckResult:
    items: list[HealthCheckItem] = field(default_factory=list)

    @property
    def healthy(self) -> bool:
        """`True` se nenhum item estiver `FAILED` — `SKIPPED` não conta
        como problema, só como "nada para checar"."""
        return all(item.status != HealthCheckStatus.FAILED for item in self.items)


def _check_model_runtime() -> HealthCheckItem:
    try:
        available = OllamaProvider().is_available()
    except Exception as exc:  # runtime indisponível não deve derrubar o health check
        return HealthCheckItem("modelo/runtime", HealthCheckStatus.FAILED, str(exc))
    if available:
        return HealthCheckItem("modelo/runtime", HealthCheckStatus.OK)
    return HealthCheckItem(
        "modelo/runtime", HealthCheckStatus.FAILED, "Ollama local indisponível"
    )


def _check_postgres() -> HealthCheckItem:
    try:
        with connect() as conn:
            conn.execute("SELECT 1")
    except Exception as exc:
        return HealthCheckItem("postgresql", HealthCheckStatus.FAILED, str(exc))
    return HealthCheckItem("postgresql", HealthCheckStatus.OK)


def _check_queue() -> HealthCheckItem:
    try:
        list_queue_items()
    except Exception as exc:
        return HealthCheckItem("fila", HealthCheckStatus.FAILED, str(exc))
    return HealthCheckItem("fila", HealthCheckStatus.OK)


def _check_tools_and_providers() -> HealthCheckItem:
    return HealthCheckItem(
        "ferramentas/providers principais",
        HealthCheckStatus.SKIPPED,
        "nenhuma ferramenta implementada ainda (Tool Registry, TASK-088+)",
    )


def _check_critical_config() -> HealthCheckItem:
    problems: list[str] = []
    if not os.environ.get("CLAUDIAO_ACTIVE_MODEL"):
        problems.append("CLAUDIAO_ACTIVE_MODEL não configurado")
    try:
        load_or_create_master_key()
    except MasterKeyPathNotConfiguredError:
        problems.append("CLAUDIAO_MASTER_KEY_PATH não configurado")
    except OSError as exc:
        problems.append(f"chave mestra inacessível: {exc}")
    if problems:
        return HealthCheckItem(
            "configurações críticas", HealthCheckStatus.FAILED, "; ".join(problems)
        )
    return HealthCheckItem("configurações críticas", HealthCheckStatus.OK)


def run_health_check() -> HealthCheckResult:
    """Roda todas as checagens (TASK-085) e registra o resultado no
    logging estruturado — item por item que falhar (`ERROR`), mais um
    resumo (`INFO`/`WARNING`)."""
    result = HealthCheckResult(
        items=[
            _check_model_runtime(),
            _check_postgres(),
            _check_queue(),
            _check_tools_and_providers(),
            _check_critical_config(),
        ]
    )

    for item in result.items:
        if item.status == HealthCheckStatus.FAILED:
            _logger.error("health check falhou: %s (%s)", item.name, item.detail)

    if result.healthy:
        _logger.info("health check: saudável")
    else:
        _logger.warning("health check: não saudável")

    return result
