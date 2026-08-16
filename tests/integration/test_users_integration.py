"""Teste de integração: cria e autentica usuários de verdade no PostgreSQL local
(TASK-009). Usa a fixture `postgres_dsn` (tests/integration/conftest.py) — pula
automaticamente se o banco não estiver disponível.
"""

import uuid

import psycopg
import pytest

from app.auth.users import (
    InvalidRoleError,
    UserAlreadyExistsError,
    authenticate_user,
    create_user,
)


@pytest.fixture
def unique_username(postgres_dsn):
    """Username isolado por execução, e limpeza garantida ao final do teste."""
    username = f"teste_task009_{uuid.uuid4().hex[:12]}"
    yield username
    with psycopg.connect(postgres_dsn) as conn:
        conn.execute("DELETE FROM users WHERE username = %s", (username,))


def test_create_user_persists_with_hashed_password(postgres_dsn, unique_username):
    user = create_user(unique_username, "senha-correta", "USER")

    assert user.username == unique_username
    assert user.role == "USER"

    with psycopg.connect(postgres_dsn) as conn:
        row = conn.execute(
            "SELECT password_hash FROM users WHERE username = %s", (unique_username,)
        ).fetchone()
    assert row is not None
    (password_hash,) = row
    assert password_hash != "senha-correta"  # nunca em texto plano
    assert password_hash.startswith("pbkdf2_sha256$")


def test_create_user_rejects_invalid_role(postgres_dsn, unique_username):
    with pytest.raises(InvalidRoleError):
        create_user(unique_username, "senha-correta", "SUPERUSER")


def test_create_user_rejects_duplicate_username(postgres_dsn, unique_username):
    create_user(unique_username, "senha-correta", "USER")

    with pytest.raises(UserAlreadyExistsError):
        create_user(unique_username, "outra-senha", "ADMIN")


def test_authenticate_user_with_correct_password(postgres_dsn, unique_username):
    create_user(unique_username, "senha-correta", "ADMIN")

    user = authenticate_user(unique_username, "senha-correta")

    assert user is not None
    assert user.username == unique_username
    assert user.role == "ADMIN"


def test_authenticate_user_with_wrong_password_returns_none(postgres_dsn, unique_username):
    create_user(unique_username, "senha-correta", "USER")

    assert authenticate_user(unique_username, "senha-errada") is None


def test_authenticate_user_unknown_username_returns_none(postgres_dsn):
    assert authenticate_user("usuario-que-nao-existe-de-jeito-nenhum", "qualquer") is None
