"""Logging local rotativo do Claudião (TASK-005).

Cobre somente o log em arquivo local, com rotação automática, conforme
docs/OBSERVABILITY.md. O logging estruturado no PostgreSQL é escopo da TASK-006,
não implementado aqui.
"""

from __future__ import annotations

import logging
import logging.handlers
import os
from pathlib import Path

DEFAULT_LOG_DIR = "logs"
DEFAULT_LOG_FILE = "claudiao.log"
DEFAULT_LEVEL = "INFO"
MAX_BYTES = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5

_VALID_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR"}

_configured = False


def _resolve_level(raw: str | None) -> int:
    level_name = (raw or DEFAULT_LEVEL).strip().upper()
    if level_name not in _VALID_LEVELS:
        level_name = DEFAULT_LEVEL
    return getattr(logging, level_name)


def configure_logging(*, force: bool = False) -> logging.Logger:
    """Configura o logger raiz do Claudião com rotação em arquivo local.

    Lê `CLAUDIAO_LOG_LEVEL`, `CLAUDIAO_LOG_DIR` e `CLAUDIAO_LOG_FILE` do ambiente
    (docs/ARCHITECTURE.md, "Configuração central"). DEBUG fica desativado por
    padrão (docs/OBSERVABILITY.md) — só ativa se `CLAUDIAO_LOG_LEVEL=DEBUG` for
    definido explicitamente. Idempotente: chamadas repetidas não duplicam handlers,
    a menos que `force=True`.
    """
    global _configured
    root = logging.getLogger("claudiao")
    if _configured and not force:
        return root

    level = _resolve_level(os.environ.get("CLAUDIAO_LOG_LEVEL"))
    log_dir = Path(os.environ.get("CLAUDIAO_LOG_DIR", DEFAULT_LOG_DIR))
    log_file = os.environ.get("CLAUDIAO_LOG_FILE", DEFAULT_LOG_FILE)
    log_dir.mkdir(parents=True, exist_ok=True)

    handler = logging.handlers.RotatingFileHandler(
        log_dir / log_file,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )
    )

    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)
    root.propagate = False

    _configured = True
    return root


def get_logger(name: str) -> logging.Logger:
    """Retorna um logger filho de `claudiao`, configurando o logging se necessário."""
    configure_logging()
    return logging.getLogger(f"claudiao.{name}")
