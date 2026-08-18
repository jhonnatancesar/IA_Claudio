"""Teste de integração: versionamento de conhecimento (TASK-054) contra o
PostgreSQL local. Usa a fixture `postgres_dsn`
(tests/integration/conftest.py) — pula automaticamente se o banco não
estiver disponível.
"""

import uuid

import psycopg
import pytest

from app.knowledge.knowledge_model import (
    KnowledgeNotFoundError,
    KnowledgeStatus,
    KnowledgeVersionConflictError,
    create_new_version,
    get_current_version,
    list_version_history,
    save_knowledge,
)


@pytest.fixture
def created_knowledge(postgres_dsn):
    knowledge = save_knowledge(f"fato de teste {uuid.uuid4().hex[:12]}")
    yield knowledge
    with psycopg.connect(postgres_dsn) as conn:
        conn.execute("DELETE FROM knowledge WHERE root_id = %s", (knowledge.root_id,))


def test_save_knowledge_starts_as_version_one_and_current(postgres_dsn, created_knowledge):
    assert created_knowledge.version == 1
    assert created_knowledge.is_current is True
    assert created_knowledge.root_id == created_knowledge.id
    assert created_knowledge.previous_version_id is None
    assert created_knowledge.change_reason is None


def test_create_new_version_creates_version_two_as_raw(postgres_dsn, created_knowledge):
    new_version = create_new_version(
        created_knowledge.id, "conteúdo atualizado", "correção de erro"
    )

    assert new_version.version == 2
    assert new_version.is_current is True
    assert new_version.status == KnowledgeStatus.RAW
    assert new_version.previous_version_id == created_knowledge.id
    assert new_version.change_reason == "correção de erro"
    assert new_version.root_id == created_knowledge.root_id


def test_create_new_version_marks_previous_as_not_current(postgres_dsn, created_knowledge):
    create_new_version(created_knowledge.id, "conteúdo atualizado", "correção")

    from app.knowledge.knowledge_model import get_knowledge

    old = get_knowledge(created_knowledge.id)
    assert old.is_current is False


def test_get_current_version_returns_latest(postgres_dsn, created_knowledge):
    new_version = create_new_version(created_knowledge.id, "conteúdo v2", "atualização")

    current = get_current_version(created_knowledge.root_id)

    assert current.id == new_version.id
    assert current.content == "conteúdo v2"


def test_list_version_history_returns_all_versions_in_order(postgres_dsn, created_knowledge):
    v2 = create_new_version(created_knowledge.id, "conteúdo v2", "motivo 1")
    v3 = create_new_version(v2.id, "conteúdo v3", "motivo 2")

    history = list_version_history(created_knowledge.root_id)

    assert [entry.id for entry in history] == [created_knowledge.id, v2.id, v3.id]
    assert [entry.version for entry in history] == [1, 2, 3]


def test_create_new_version_rejects_non_current_version(postgres_dsn, created_knowledge):
    create_new_version(created_knowledge.id, "conteúdo v2", "motivo")

    with pytest.raises(KnowledgeVersionConflictError):
        create_new_version(created_knowledge.id, "conteúdo v3 inválido", "motivo")


def test_create_new_version_raises_for_unknown_id(postgres_dsn):
    with pytest.raises(KnowledgeNotFoundError):
        create_new_version(uuid.uuid4(), "conteúdo", "motivo")


def test_get_current_version_returns_none_for_unknown_root(postgres_dsn):
    assert get_current_version(uuid.uuid4()) is None
