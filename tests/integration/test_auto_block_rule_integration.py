"""Teste de integração: bloqueio automático de fontes (TASK-065) contra o
PostgreSQL local. Usa a fixture `postgres_dsn`
(tests/conftest.py) — pula automaticamente se o banco não
estiver disponível.
"""

import uuid

import psycopg
import pytest

from app.sources.auto_block_rule import AUTO_BLOCK_REASON, auto_block_after_validation
from app.sources.source_registry import (
    BlacklistAction,
    BlockOrigin,
    SourceReputation,
    list_blacklist_entries,
    register_source,
)


@pytest.fixture
def unique_identifier():
    return f"exemplo-{uuid.uuid4().hex[:12]}.com"


@pytest.fixture(autouse=True)
def cleanup(postgres_dsn, unique_identifier):
    yield
    with psycopg.connect(postgres_dsn) as conn:
        conn.execute("DELETE FROM sources WHERE identifier = %s", (unique_identifier,))


def test_auto_block_triggers_when_reputation_drops_to_low(postgres_dsn, unique_identifier):
    source = register_source(unique_identifier, reputation=SourceReputation.MEDIUM)

    updated = auto_block_after_validation(source.id, was_accurate=False)

    assert updated.reputation == SourceReputation.LOW
    assert updated.is_blocked is True
    entries = list_blacklist_entries(source.id)
    assert len(entries) == 1
    assert entries[0].action == BlacklistAction.BLOCK
    assert entries[0].origin == BlockOrigin.AGENT
    assert entries[0].reason == AUTO_BLOCK_REASON


def test_auto_block_does_not_trigger_when_reputation_stays_above_low(
    postgres_dsn, unique_identifier
):
    source = register_source(unique_identifier, reputation=SourceReputation.HIGH)

    updated = auto_block_after_validation(source.id, was_accurate=False)

    assert updated.reputation == SourceReputation.MEDIUM
    assert updated.is_blocked is False
    assert list_blacklist_entries(source.id) == []


def test_auto_block_does_not_duplicate_block_when_already_blocked(
    postgres_dsn, unique_identifier
):
    source = register_source(unique_identifier, reputation=SourceReputation.LOW)

    auto_block_after_validation(source.id, was_accurate=False)
    updated_again = auto_block_after_validation(source.id, was_accurate=False)

    assert updated_again.is_blocked is True
    assert len(list_blacklist_entries(source.id)) == 1


def test_auto_block_accurate_result_does_not_block(postgres_dsn, unique_identifier):
    source = register_source(unique_identifier, reputation=SourceReputation.MEDIUM)

    updated = auto_block_after_validation(source.id, was_accurate=True)

    assert updated.reputation == SourceReputation.HIGH
    assert updated.is_blocked is False
