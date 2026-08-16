"""Conexão com o PostgreSQL local a partir da configuração central
(TASK-002/TASK-003). DSN montada a partir de `CLAUDIAO_POSTGRES_*`
(docs/ARCHITECTURE.md). Usado por qualquer módulo que precise falar com o banco
(logging estruturado — TASK-006; autenticação — TASK-009; e os que vierem
depois).

Movido para cá na TASK-009 a partir de
`app.observability.postgres_log_handler` (que só tinha essa lógica porque foi o
primeiro consumidor, na TASK-006) para evitar duplicar a montagem de DSN quando
um segundo consumidor (autenticação) precisou dela. Nenhuma mudança de
comportamento — só de local.
"""

from __future__ import annotations

import os

import psycopg


def build_dsn_from_env() -> str | None:
    """Monta a DSN a partir de `CLAUDIAO_POSTGRES_*` (docs/ARCHITECTURE.md).

    Retorna `None` se alguma variável obrigatória estiver ausente — quem chama
    decide o que fazer (ex.: não anexar um handler, ou levantar um erro próprio).
    """
    host = os.environ.get("CLAUDIAO_POSTGRES_HOST")
    port = os.environ.get("CLAUDIAO_POSTGRES_PORT")
    db = os.environ.get("CLAUDIAO_POSTGRES_DB")
    user = os.environ.get("CLAUDIAO_POSTGRES_USER")
    password = os.environ.get("CLAUDIAO_POSTGRES_PASSWORD")
    if not all([host, port, db, user, password]):
        return None
    return f"host={host} port={port} dbname={db} user={user} password={password}"


def connect() -> psycopg.Connection:
    """Abre uma conexão nova com o banco, a partir da configuração central.

    Levanta `RuntimeError` se `CLAUDIAO_POSTGRES_*` não estiver configurado —
    diferente de `build_dsn_from_env()`, que só retorna `None` (usado por quem
    pode funcionar sem banco, como o logging).
    """
    dsn = build_dsn_from_env()
    if dsn is None:
        raise RuntimeError(
            "Configuração do PostgreSQL (CLAUDIAO_POSTGRES_*) ausente — "
            "ver config/.env.example."
        )
    return psycopg.connect(dsn)
