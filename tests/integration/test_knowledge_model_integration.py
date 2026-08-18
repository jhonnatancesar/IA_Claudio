"""Teste de integração: persiste e transiciona conhecimento de verdade no
PostgreSQL local (TASK-052). Usa a fixture `postgres_dsn`
(tests/integration/conftest.py) — pula automaticamente se o banco não
estiver disponível.
"""

import uuid

import psycopg
import pytest

from app.knowledge.knowledge_model import (
    InvalidKnowledgeStatusTransitionError,
    KnowledgeNotFoundError,
    KnowledgeStatus,
    advance_knowledge_status,
    get_knowledge,
    save_knowledge,
)


@pytest.fixture
def created_knowledge(postgres_dsn):
    """Um conhecimento novo (`RAW`), com limpeza garantida ao final."""
    knowledge = save_knowledge(f"fato de teste {uuid.uuid4().hex[:12]}")
    yield knowledge
    with psycopg.connect(postgres_dsn) as conn:
        conn.execute("DELETE FROM knowledge WHERE id = %s", (knowledge.id,))


def test_save_knowledge_starts_as_raw(postgres_dsn, created_knowledge):
    assert created_knowledge.status == KnowledgeStatus.RAW


def test_save_knowledge_persists_and_is_readable_by_id(postgres_dsn, created_knowledge):
    fetched = get_knowledge(created_knowledge.id)

    assert fetched is not None
    assert fetched.content == created_knowledge.content
    assert fetched.status == KnowledgeStatus.RAW


def test_get_knowledge_returns_none_for_unknown_id(postgres_dsn):
    assert get_knowledge(uuid.uuid4()) is None


def test_advance_knowledge_status_raw_to_provisional(postgres_dsn, created_knowledge):
    updated = advance_knowledge_status(created_knowledge.id, KnowledgeStatus.PROVISIONAL)

    assert updated.status == KnowledgeStatus.PROVISIONAL
    assert get_knowledge(created_knowledge.id).status == KnowledgeStatus.PROVISIONAL


def test_advance_knowledge_status_provisional_to_confirmed(postgres_dsn, created_knowledge):
    advance_knowledge_status(created_knowledge.id, KnowledgeStatus.PROVISIONAL)

    updated = advance_knowledge_status(created_knowledge.id, KnowledgeStatus.CONFIRMED)

    assert updated.status == KnowledgeStatus.CONFIRMED


def test_advance_knowledge_status_rejects_skipping_provisional(postgres_dsn, created_knowledge):
    with pytest.raises(InvalidKnowledgeStatusTransitionError):
        advance_knowledge_status(created_knowledge.id, KnowledgeStatus.CONFIRMED)


def test_advance_knowledge_status_rejects_repeating_same_status(postgres_dsn, created_knowledge):
    with pytest.raises(InvalidKnowledgeStatusTransitionError):
        advance_knowledge_status(created_knowledge.id, KnowledgeStatus.RAW)


def test_advance_knowledge_status_rejects_going_backwards(postgres_dsn, created_knowledge):
    advance_knowledge_status(created_knowledge.id, KnowledgeStatus.PROVISIONAL)
    advance_knowledge_status(created_knowledge.id, KnowledgeStatus.CONFIRMED)

    with pytest.raises(InvalidKnowledgeStatusTransitionError):
        advance_knowledge_status(created_knowledge.id, KnowledgeStatus.PROVISIONAL)


def test_advance_knowledge_status_raises_for_unknown_id(postgres_dsn):
    with pytest.raises(KnowledgeNotFoundError):
        advance_knowledge_status(uuid.uuid4(), KnowledgeStatus.PROVISIONAL)
