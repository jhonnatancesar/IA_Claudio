"""Teste de integração: cria e autentica aplicações de verdade no PostgreSQL
local (TASK-011). Usa a fixture `postgres_dsn`
(tests/integration/conftest.py) — pula automaticamente se o banco não estiver
disponível.
"""

import uuid

import psycopg
import pytest

from app.auth.api_keys import (
    ApplicationAlreadyExistsError,
    authenticate_application,
    create_application,
)


@pytest.fixture
def unique_app_name(postgres_dsn):
    """Nome de aplicação isolado por execução, com limpeza garantida."""
    name = f"teste_task011_{uuid.uuid4().hex[:12]}"
    yield name
    with psycopg.connect(postgres_dsn) as conn:
        conn.execute("DELETE FROM applications WHERE name = %s", (name,))


def test_create_application_returns_plaintext_key_once(postgres_dsn, unique_app_name):
    application, api_key = create_application(unique_app_name)

    assert application.name == unique_app_name
    assert api_key.startswith("cldk_")


def test_create_application_never_stores_plaintext_key(postgres_dsn, unique_app_name):
    _application, api_key = create_application(unique_app_name)

    with psycopg.connect(postgres_dsn) as conn:
        row = conn.execute(
            "SELECT api_key_hash FROM applications WHERE name = %s",
            (unique_app_name,),
        ).fetchone()
    assert row is not None
    (api_key_hash,) = row
    assert api_key_hash != api_key
    assert len(api_key_hash) == 64  # sha256 em hex


def test_create_application_rejects_duplicate_name(postgres_dsn, unique_app_name):
    create_application(unique_app_name)

    with pytest.raises(ApplicationAlreadyExistsError):
        create_application(unique_app_name)


def test_authenticate_application_with_correct_key(postgres_dsn, unique_app_name):
    application, api_key = create_application(unique_app_name)

    authenticated = authenticate_application(api_key)

    assert authenticated is not None
    assert authenticated.id == application.id
    assert authenticated.name == unique_app_name


def test_authenticate_application_with_wrong_key_returns_none(postgres_dsn, unique_app_name):
    create_application(unique_app_name)

    assert authenticate_application("cldk_chave-completamente-errada") is None


def test_authenticate_application_with_empty_key_returns_none(postgres_dsn):
    assert authenticate_application("") is None
