"""Teste de integração: blacklist de fontes (TASK-064) contra o
PostgreSQL local. Usa a fixture `postgres_dsn`
(tests/conftest.py) — pula automaticamente se o banco não
estiver disponível.
"""

import uuid

import psycopg
import pytest

from app.sources.source_registry import (
    BlacklistAction,
    BlockOrigin,
    SourceBlacklistStateError,
    SourceNotFoundError,
    block_source,
    get_source,
    list_blacklist_entries,
    register_source,
    unblock_source,
)


@pytest.fixture
def unique_identifier():
    return f"exemplo-{uuid.uuid4().hex[:12]}.com"


@pytest.fixture(autouse=True)
def cleanup(postgres_dsn, unique_identifier):
    yield
    with psycopg.connect(postgres_dsn) as conn:
        conn.execute("DELETE FROM sources WHERE identifier = %s", (unique_identifier,))


def test_register_source_starts_unblocked(postgres_dsn, unique_identifier):
    source = register_source(unique_identifier)

    assert source.is_blocked is False


def test_block_source_marks_blocked_and_records_entry(postgres_dsn, unique_identifier):
    source = register_source(unique_identifier)

    blocked = block_source(source.id, BlockOrigin.ADMIN, "conteúdo enganoso", responsible="admin1")

    assert blocked.is_blocked is True
    entries = list_blacklist_entries(source.id)
    assert len(entries) == 1
    assert entries[0].action == BlacklistAction.BLOCK
    assert entries[0].origin == BlockOrigin.ADMIN
    assert entries[0].responsible == "admin1"
    assert entries[0].reason == "conteúdo enganoso"


def test_block_source_agent_origin_without_responsible(postgres_dsn, unique_identifier):
    source = register_source(unique_identifier)

    blocked = block_source(source.id, BlockOrigin.AGENT, "dados contraditórios detectados")

    entries = list_blacklist_entries(blocked.id)
    assert entries[0].origin == BlockOrigin.AGENT
    assert entries[0].responsible is None


def test_block_source_rejects_already_blocked(postgres_dsn, unique_identifier):
    source = register_source(unique_identifier)
    block_source(source.id, BlockOrigin.ADMIN, "motivo 1")

    with pytest.raises(SourceBlacklistStateError):
        block_source(source.id, BlockOrigin.ADMIN, "motivo 2")


def test_block_source_raises_for_unknown_id(postgres_dsn):
    with pytest.raises(SourceNotFoundError):
        block_source(uuid.uuid4(), BlockOrigin.ADMIN, "motivo")


def test_unblock_source_marks_unblocked_and_records_entry(postgres_dsn, unique_identifier):
    source = register_source(unique_identifier)
    block_source(source.id, BlockOrigin.AGENT, "validação automática")

    unblocked = unblock_source(source.id, BlockOrigin.ADMIN, "revisado manualmente", responsible="admin1")

    assert unblocked.is_blocked is False
    assert get_source(source.id).is_blocked is False
    entries = list_blacklist_entries(source.id)
    assert len(entries) == 2
    assert entries[1].action == BlacklistAction.UNBLOCK
    assert entries[1].responsible == "admin1"


def test_unblock_source_rejects_not_blocked(postgres_dsn, unique_identifier):
    source = register_source(unique_identifier)

    with pytest.raises(SourceBlacklistStateError):
        unblock_source(source.id, BlockOrigin.ADMIN, "motivo")


def test_unblock_source_raises_for_unknown_id(postgres_dsn):
    with pytest.raises(SourceNotFoundError):
        unblock_source(uuid.uuid4(), BlockOrigin.ADMIN, "motivo")


def test_list_blacklist_entries_empty_when_never_blocked(postgres_dsn, unique_identifier):
    source = register_source(unique_identifier)

    assert list_blacklist_entries(source.id) == []


def test_list_blacklist_entries_chronological_order(postgres_dsn, unique_identifier):
    source = register_source(unique_identifier)
    block_source(source.id, BlockOrigin.AGENT, "motivo bloqueio")
    unblock_source(source.id, BlockOrigin.ADMIN, "motivo desbloqueio")

    entries = list_blacklist_entries(source.id)

    assert [e.action for e in entries] == [BlacklistAction.BLOCK, BlacklistAction.UNBLOCK]
