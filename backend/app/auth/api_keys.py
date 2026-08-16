"""Autenticação de aplicações via API key (TASK-011).

Diferente de senha de usuário (TASK-009, PBKDF2 lento e salgado), a API key já
nasce com alta entropia (gerada aleatoriamente, nunca escolhida por humano) — o
hash aqui é SHA-256 simples, sem salt nem iterações lentas: não há risco de
força bruta por dicionário sobre um segredo de 256 bits, e um hash rápido é o
esperado para lookup por igualdade. A API key em texto plano só existe no
momento da criação — depois só o hash fica no banco (docs/DATABASE.md).
"""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from uuid import UUID

import psycopg

from app.db.connection import connect

_API_KEY_ENTROPY_BYTES = 32  # 256 bits
_API_KEY_PREFIX = "cldk_"  # prefixo p/ reconhecer visualmente uma API key do Claudião


class ApplicationAlreadyExistsError(ValueError):
    """Levantado ao tentar criar uma aplicação com `name` já existente."""


@dataclass(frozen=True)
class Application:
    id: UUID
    name: str


def _hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def generate_api_key() -> str:
    """Gera uma API key nova, aleatória (256 bits de entropia), com prefixo
    reconhecível visualmente."""
    return _API_KEY_PREFIX + secrets.token_urlsafe(_API_KEY_ENTROPY_BYTES)


def create_application(name: str) -> tuple[Application, str]:
    """Cria uma aplicação nova. Retorna a aplicação e a API key em **texto
    plano** — essa é a única vez que o texto plano é exposto; só o hash é
    persistido, sem forma de recuperar a key original depois. Levanta
    `ApplicationAlreadyExistsError` para `name` duplicado."""
    if not name or not name.strip():
        raise ValueError("name não pode ser vazio")

    api_key = generate_api_key()
    api_key_hash = _hash_api_key(api_key)
    with connect() as conn:
        try:
            row = conn.execute(
                "INSERT INTO applications (name, api_key_hash) VALUES (%s, %s) "
                "RETURNING id, name",
                (name, api_key_hash),
            ).fetchone()
        except psycopg.errors.UniqueViolation as exc:
            raise ApplicationAlreadyExistsError(
                f"aplicação já existe: {name!r}"
            ) from exc

    application_id, db_name = row
    return Application(id=application_id, name=db_name), api_key


def authenticate_application(api_key: str) -> Application | None:
    """Autentica por API key. Retorna `None` para key vazia ou desconhecida —
    sem distinguir os dois casos na resposta."""
    if not api_key:
        return None
    api_key_hash = _hash_api_key(api_key)
    with connect() as conn:
        row = conn.execute(
            "SELECT id, name FROM applications WHERE api_key_hash = %s",
            (api_key_hash,),
        ).fetchone()
    if row is None:
        return None
    application_id, name = row
    return Application(id=application_id, name=name)
