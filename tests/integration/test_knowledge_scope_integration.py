"""Teste de integração: escopo GLOBAL/APPLICATION de conhecimento
(TASK-055) contra o PostgreSQL local. Usa a fixture `postgres_dsn`
(tests/integration/conftest.py) — pula automaticamente se o banco não
estiver disponível.
"""

import uuid

import psycopg
import pytest

from app.knowledge.knowledge_model import (
    KnowledgeScope,
    create_new_version,
    list_knowledge_for_scope,
    save_knowledge,
)


@pytest.fixture
def cleanup_root_ids(postgres_dsn):
    root_ids: list = []
    yield root_ids
    with psycopg.connect(postgres_dsn) as conn:
        for root_id in root_ids:
            conn.execute("DELETE FROM knowledge WHERE root_id = %s", (root_id,))


def test_save_knowledge_defaults_to_global_scope(postgres_dsn, cleanup_root_ids):
    knowledge = save_knowledge(f"fato {uuid.uuid4().hex[:8]}")
    cleanup_root_ids.append(knowledge.root_id)

    assert knowledge.scope_type == KnowledgeScope.GLOBAL
    assert knowledge.scope_id is None


def test_save_knowledge_with_application_scope(postgres_dsn, cleanup_root_ids):
    knowledge = save_knowledge(
        f"fato {uuid.uuid4().hex[:8]}", scope_type=KnowledgeScope.APPLICATION, scope_id="app-42"
    )
    cleanup_root_ids.append(knowledge.root_id)

    assert knowledge.scope_type == KnowledgeScope.APPLICATION
    assert knowledge.scope_id == "app-42"


def test_create_new_version_inherits_scope(postgres_dsn, cleanup_root_ids):
    knowledge = save_knowledge(
        f"fato {uuid.uuid4().hex[:8]}", scope_type=KnowledgeScope.APPLICATION, scope_id="app-42"
    )
    cleanup_root_ids.append(knowledge.root_id)

    new_version = create_new_version(knowledge.id, "fato atualizado", "correção")

    assert new_version.scope_type == KnowledgeScope.APPLICATION
    assert new_version.scope_id == "app-42"


def test_list_knowledge_for_scope_global_excludes_application(postgres_dsn, cleanup_root_ids):
    marker = uuid.uuid4().hex[:8]
    global_knowledge = save_knowledge(f"global {marker}")
    app_knowledge = save_knowledge(
        f"app {marker}", scope_type=KnowledgeScope.APPLICATION, scope_id=f"app-{marker}"
    )
    cleanup_root_ids.append(global_knowledge.root_id)
    cleanup_root_ids.append(app_knowledge.root_id)

    results = list_knowledge_for_scope(KnowledgeScope.GLOBAL)

    result_ids = {k.id for k in results}
    assert global_knowledge.id in result_ids
    assert app_knowledge.id not in result_ids


def test_list_knowledge_for_scope_application_isolates_by_scope_id(
    postgres_dsn, cleanup_root_ids
):
    marker = uuid.uuid4().hex[:8]
    knowledge_a = save_knowledge(
        f"fato A {marker}", scope_type=KnowledgeScope.APPLICATION, scope_id=f"app-a-{marker}"
    )
    knowledge_b = save_knowledge(
        f"fato B {marker}", scope_type=KnowledgeScope.APPLICATION, scope_id=f"app-b-{marker}"
    )
    cleanup_root_ids.append(knowledge_a.root_id)
    cleanup_root_ids.append(knowledge_b.root_id)

    results = list_knowledge_for_scope(KnowledgeScope.APPLICATION, scope_id=f"app-a-{marker}")

    assert [k.id for k in results] == [knowledge_a.id]


def test_list_knowledge_for_scope_only_returns_current_version(postgres_dsn, cleanup_root_ids):
    marker = uuid.uuid4().hex[:8]
    knowledge = save_knowledge(f"fato {marker}")
    cleanup_root_ids.append(knowledge.root_id)
    new_version = create_new_version(knowledge.id, f"fato {marker} atualizado", "correção")

    results = list_knowledge_for_scope(KnowledgeScope.GLOBAL)

    matching = [k for k in results if k.root_id == knowledge.root_id]
    assert [k.id for k in matching] == [new_version.id]
