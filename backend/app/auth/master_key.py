"""Chave mestra de criptografia, externa ao PostgreSQL (TASK-013).

A chave nunca fica no banco nem versionada no Git (`.gitignore` cobre
`master.key`/`*.master-key`). Fica em arquivo protegido na máquina, cujo
caminho vem de `CLAUDIAO_MASTER_KEY_PATH` (`config/.env.example`, TASK-002). Se
o arquivo não existir, uma chave nova é gerada (`app.auth.crypto.generate_key`)
e persistida ali — a primeira inicialização funciona sem passo manual
obrigatório, mas o arquivo, uma vez criado, é a fonte de verdade permanente.
"""

from __future__ import annotations

import os
import stat
from pathlib import Path

from app.auth.crypto import generate_key

_ENV_VAR = "CLAUDIAO_MASTER_KEY_PATH"


class MasterKeyPathNotConfiguredError(RuntimeError):
    """Levantado quando nenhum caminho é informado nem `CLAUDIAO_MASTER_KEY_PATH`
    está definida."""


def _resolve_path() -> Path:
    raw_path = os.environ.get(_ENV_VAR)
    if not raw_path:
        raise MasterKeyPathNotConfiguredError(
            f"{_ENV_VAR} não definida — ver config/.env.example."
        )
    return Path(raw_path)


def _restrict_permissions(path: Path) -> None:
    """Restringe a permissão do arquivo, melhor esforço conforme o SO.

    Em POSIX, restringe leitura/escrita ao dono. No **Windows** (ambiente de
    referência da V1 — `docs/ARCHITECTURE.md`), `os.chmod` só alcança a flag
    somente-leitura — não é uma ACL de verdade restringindo por usuário. Uma
    proteção completa exigiria uma dependência nova (ex.: `pywin32`) só para
    isso, o que não se justifica nesta TASK — **lacuna conhecida**, registrada
    em `docs/SECURITY.md`.
    """
    try:
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass


def load_or_create_master_key(path: str | Path | None = None) -> bytes:
    """Carrega a chave mestra do arquivo protegido; se o arquivo não existir,
    gera uma chave nova e a persiste ali.

    `path` explícito tem prioridade; sem ele, usa `CLAUDIAO_MASTER_KEY_PATH`.
    Levanta `MasterKeyPathNotConfiguredError` se nenhum dos dois estiver
    disponível.
    """
    key_path = Path(path) if path is not None else _resolve_path()

    if key_path.exists():
        return key_path.read_bytes()

    key = generate_key()
    key_path.parent.mkdir(parents=True, exist_ok=True)
    key_path.write_bytes(key)
    _restrict_permissions(key_path)
    return key
