"""Teste de integração: cadastro de fontes (TASK-059) contra o
PostgreSQL local. Usa a fixture `postgres_dsn`
(tests/integration/conftest.py) — pula automaticamente se o banco não
estiver disponível.
"""

import uuid

import psycopg
import pytest

from app.sources.source_registry import (
    SourceNotFoundError,
    SourceReputation,
    SourceType,
    get_source,
    get_source_by_identifier,
    register_source,
    set_source_reputation,
    set_source_type,
)


@pytest.fixture
def unique_identifier():
    return f"exemplo-{uuid.uuid4().hex[:12]}.com"


@pytest.fixture(autouse=True)
def cleanup(postgres_dsn, unique_identifier):
    yield
    with psycopg.connect(postgres_dsn) as conn:
        conn.execute("DELETE FROM sources WHERE identifier = %s", (unique_identifier,))


def test_register_source_persists_and_is_readable_by_id(postgres_dsn, unique_identifier):
    source = register_source(unique_identifier)

    fetched = get_source(source.id)

    assert fetched is not None
    assert fetched.identifier == unique_identifier


def test_register_source_is_idempotent_by_identifier(postgres_dsn, unique_identifier):
    first = register_source(unique_identifier)
    second = register_source(unique_identifier)

    assert first.id == second.id


def test_get_source_returns_none_for_unknown_id(postgres_dsn):
    assert get_source(uuid.uuid4()) is None


def test_get_source_by_identifier_returns_none_when_not_registered(
    postgres_dsn, unique_identifier
):
    assert get_source_by_identifier(unique_identifier) is None


def test_get_source_by_identifier_finds_registered_source(postgres_dsn, unique_identifier):
    registered = register_source(unique_identifier)

    fetched = get_source_by_identifier(unique_identifier)

    assert fetched is not None
    assert fetched.id == registered.id


def test_register_source_defaults_to_unknown_type(postgres_dsn, unique_identifier):
    source = register_source(unique_identifier)

    assert source.source_type == SourceType.UNKNOWN


def test_register_source_accepts_explicit_type(postgres_dsn, unique_identifier):
    source = register_source(unique_identifier, source_type=SourceType.PRIMARY)

    assert source.source_type == SourceType.PRIMARY


def test_set_source_type_reclassifies_existing_source(postgres_dsn, unique_identifier):
    source = register_source(unique_identifier)

    updated = set_source_type(source.id, SourceType.SECONDARY)

    assert updated.source_type == SourceType.SECONDARY
    assert get_source(source.id).source_type == SourceType.SECONDARY


def test_set_source_type_raises_for_unknown_id(postgres_dsn):
    with pytest.raises(SourceNotFoundError):
        set_source_type(uuid.uuid4(), SourceType.PRIMARY)


def test_register_source_defaults_to_medium_reputation(postgres_dsn, unique_identifier):
    source = register_source(unique_identifier)

    assert source.reputation == SourceReputation.MEDIUM


def test_register_source_accepts_explicit_reputation(postgres_dsn, unique_identifier):
    source = register_source(unique_identifier, reputation=SourceReputation.HIGH)

    assert source.reputation == SourceReputation.HIGH


def test_set_source_reputation_updates_existing_source(postgres_dsn, unique_identifier):
    source = register_source(unique_identifier)

    updated = set_source_reputation(source.id, SourceReputation.LOW)

    assert updated.reputation == SourceReputation.LOW
    assert get_source(source.id).reputation == SourceReputation.LOW


def test_set_source_reputation_raises_for_unknown_id(postgres_dsn):
    with pytest.raises(SourceNotFoundError):
        set_source_reputation(uuid.uuid4(), SourceReputation.HIGH)
