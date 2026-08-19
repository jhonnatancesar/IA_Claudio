"""Teste de integração: atualização de reputação de fontes (TASK-062)
contra o PostgreSQL local. Usa a fixture `postgres_dsn`
(tests/integration/conftest.py) — pula automaticamente se o banco não
estiver disponível.
"""

import uuid

import psycopg
import pytest

from app.sources.reputation_rule import update_source_reputation
from app.sources.source_registry import SourceNotFoundError, SourceReputation, register_source


@pytest.fixture
def unique_identifier():
    return f"exemplo-{uuid.uuid4().hex[:12]}.com"


@pytest.fixture(autouse=True)
def cleanup(postgres_dsn, unique_identifier):
    yield
    with psycopg.connect(postgres_dsn) as conn:
        conn.execute("DELETE FROM sources WHERE identifier = %s", (unique_identifier,))


def test_update_source_reputation_downgrades_on_inaccurate_result(
    postgres_dsn, unique_identifier
):
    source = register_source(unique_identifier, reputation=SourceReputation.HIGH)

    updated = update_source_reputation(source.id, was_accurate=False)

    assert updated.reputation == SourceReputation.MEDIUM


def test_update_source_reputation_upgrades_on_accurate_result(
    postgres_dsn, unique_identifier
):
    source = register_source(unique_identifier, reputation=SourceReputation.MEDIUM)

    updated = update_source_reputation(source.id, was_accurate=True)

    assert updated.reputation == SourceReputation.HIGH


def test_update_source_reputation_stays_low_on_repeated_inaccuracy(
    postgres_dsn, unique_identifier
):
    source = register_source(unique_identifier, reputation=SourceReputation.LOW)

    updated = update_source_reputation(source.id, was_accurate=False)

    assert updated.reputation == SourceReputation.LOW


def test_update_source_reputation_raises_for_unknown_id(postgres_dsn):
    with pytest.raises(SourceNotFoundError):
        update_source_reputation(uuid.uuid4(), was_accurate=False)
