"""Teste de integração: desbloqueio somente ADMIN (TASK-066) contra o
PostgreSQL local. Usa a fixture `postgres_dsn`
(tests/integration/conftest.py) — pula automaticamente se o banco não
estiver disponível.
"""

import uuid

import psycopg
import pytest

from app.errors.response import ClaudiaoError
from app.sources.source_registry import (
    BlockOrigin,
    SourceBlacklistStateError,
    block_source,
    get_source,
    list_blacklist_entries,
    register_source,
)
from app.sources.unblock_rule import admin_unblock_source


@pytest.fixture
def unique_identifier():
    return f"exemplo-{uuid.uuid4().hex[:12]}.com"


@pytest.fixture(autouse=True)
def cleanup(postgres_dsn, unique_identifier):
    yield
    with psycopg.connect(postgres_dsn) as conn:
        conn.execute("DELETE FROM sources WHERE identifier = %s", (unique_identifier,))


def test_admin_unblock_succeeds_for_admin_blocked_source(postgres_dsn, unique_identifier):
    source = register_source(unique_identifier)
    block_source(source.id, BlockOrigin.ADMIN, "motivo qualquer")

    updated = admin_unblock_source(source.id, role="ADMIN", responsible="admin1", reason="revisado")

    assert updated.is_blocked is False
    assert get_source(source.id).is_blocked is False


def test_admin_unblock_succeeds_for_agent_blocked_source(postgres_dsn, unique_identifier):
    source = register_source(unique_identifier)
    block_source(source.id, BlockOrigin.AGENT, "dados contraditórios")

    updated = admin_unblock_source(source.id, role="ADMIN", responsible="admin1", reason="revisado")

    assert updated.is_blocked is False
    entries = list_blacklist_entries(source.id)
    assert entries[-1].origin == BlockOrigin.ADMIN
    assert entries[-1].responsible == "admin1"


def test_admin_unblock_rejects_user_role(postgres_dsn, unique_identifier):
    source = register_source(unique_identifier)
    block_source(source.id, BlockOrigin.AGENT, "dados contraditórios")

    with pytest.raises(ClaudiaoError):
        admin_unblock_source(source.id, role="USER", responsible="usuario1", reason="tentativa")

    assert get_source(source.id).is_blocked is True


def test_admin_unblock_rejects_empty_responsible(postgres_dsn, unique_identifier):
    source = register_source(unique_identifier)
    block_source(source.id, BlockOrigin.ADMIN, "motivo")

    with pytest.raises(ValueError):
        admin_unblock_source(source.id, role="ADMIN", responsible="", reason="motivo")


def test_admin_unblock_propagates_state_error_when_not_blocked(postgres_dsn, unique_identifier):
    source = register_source(unique_identifier)

    with pytest.raises(SourceBlacklistStateError):
        admin_unblock_source(source.id, role="ADMIN", responsible="admin1", reason="motivo")
