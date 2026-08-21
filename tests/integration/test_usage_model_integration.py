"""Teste de integração: rastreio de consumo (TASK-073) contra o
PostgreSQL local. Usa a fixture `postgres_dsn`
(tests/conftest.py) — pula automaticamente se o banco não
estiver disponível.
"""

import uuid

import psycopg
import pytest

from app.auth.api_keys import create_application
from app.usage.usage_model import (
    list_recent_usage_records,
    list_usage_for_application,
    record_usage,
)


@pytest.fixture
def registered_application(postgres_dsn):
    name = f"teste_task073_{uuid.uuid4().hex[:12]}"
    application, _ = create_application(name)
    yield application
    with psycopg.connect(postgres_dsn) as conn:
        conn.execute("DELETE FROM applications WHERE id = %s", (application.id,))


def test_record_usage_persists_and_is_listed(postgres_dsn, registered_application):
    execution_id = str(uuid.uuid4())

    record = record_usage(registered_application.id, execution_id, "COMPLETED")

    assert record.application_id == registered_application.id
    assert record.execution_id == execution_id
    assert record.status == "COMPLETED"

    listed = list_usage_for_application(registered_application.id)
    assert len(listed) == 1
    assert listed[0].id == record.id


def test_list_usage_for_application_returns_chronological_order(
    postgres_dsn, registered_application
):
    first = record_usage(registered_application.id, str(uuid.uuid4()), "COMPLETED")
    second = record_usage(registered_application.id, str(uuid.uuid4()), "FAILED")

    listed = list_usage_for_application(registered_application.id)

    assert [r.id for r in listed] == [first.id, second.id]


def test_list_usage_for_application_empty_when_no_usage_recorded(
    postgres_dsn, registered_application
):
    assert list_usage_for_application(registered_application.id) == []


def test_usage_records_removed_when_application_is_deleted(postgres_dsn):
    name = f"teste_task073_cascade_{uuid.uuid4().hex[:12]}"
    application, _ = create_application(name)
    record_usage(application.id, str(uuid.uuid4()), "COMPLETED")

    with psycopg.connect(postgres_dsn) as conn:
        conn.execute("DELETE FROM applications WHERE id = %s", (application.id,))
        remaining = conn.execute(
            "SELECT COUNT(*) FROM usage_records WHERE application_id = %s",
            (application.id,),
        ).fetchone()

    assert remaining[0] == 0


def test_list_recent_usage_records_includes_records_from_any_application(
    postgres_dsn, registered_application
):
    execution_id = str(uuid.uuid4())
    record_usage(registered_application.id, execution_id, "COMPLETED")

    listed = list_recent_usage_records(limit=50)

    assert any(r.execution_id == execution_id for r in listed)


def test_list_recent_usage_records_respects_limit(postgres_dsn):
    assert len(list_recent_usage_records(limit=1)) <= 1
