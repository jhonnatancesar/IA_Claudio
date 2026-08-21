"""Teste de integração: regra de promoção para CONFIRMED (TASK-057)
contra o PostgreSQL local. Usa a fixture `postgres_dsn`
(tests/conftest.py) — pula automaticamente se o banco não
estiver disponível.
"""

import uuid

import psycopg
import pytest

from app.knowledge.knowledge_model import (
    KnowledgeStatus,
    add_evidence,
    advance_knowledge_status,
    save_knowledge,
    set_knowledge_confidence,
)
from app.knowledge.promotion_rule import (
    KnowledgePromotionNotEligibleError,
    promote_to_confirmed,
)
from app.llm.protocol import Confidence


@pytest.fixture
def provisional_knowledge(postgres_dsn):
    knowledge = save_knowledge(f"fato de teste {uuid.uuid4().hex[:12]}")
    knowledge = advance_knowledge_status(knowledge.id, KnowledgeStatus.PROVISIONAL)
    yield knowledge
    with psycopg.connect(postgres_dsn) as conn:
        conn.execute("DELETE FROM knowledge WHERE root_id = %s", (knowledge.root_id,))


def test_promote_to_confirmed_succeeds_when_eligible(postgres_dsn, provisional_knowledge):
    set_knowledge_confidence(provisional_knowledge.id, Confidence.HIGH)
    add_evidence(provisional_knowledge.id, "fonte oficial")

    promoted = promote_to_confirmed(provisional_knowledge.id)

    assert promoted.status == KnowledgeStatus.CONFIRMED


def test_promote_to_confirmed_rejects_without_evidence(postgres_dsn, provisional_knowledge):
    set_knowledge_confidence(provisional_knowledge.id, Confidence.HIGH)

    with pytest.raises(KnowledgePromotionNotEligibleError):
        promote_to_confirmed(provisional_knowledge.id)


def test_promote_to_confirmed_rejects_low_confidence(postgres_dsn, provisional_knowledge):
    set_knowledge_confidence(provisional_knowledge.id, Confidence.MEDIUM)
    add_evidence(provisional_knowledge.id, "fonte qualquer")

    with pytest.raises(KnowledgePromotionNotEligibleError):
        promote_to_confirmed(provisional_knowledge.id)


def test_promote_to_confirmed_rejects_raw_status(postgres_dsn):
    knowledge = save_knowledge(f"fato raw {uuid.uuid4().hex[:12]}")
    set_knowledge_confidence(knowledge.id, Confidence.HIGH)
    add_evidence(knowledge.id, "fonte qualquer")

    try:
        with pytest.raises(KnowledgePromotionNotEligibleError):
            promote_to_confirmed(knowledge.id)
    finally:
        with psycopg.connect(postgres_dsn) as conn:
            conn.execute("DELETE FROM knowledge WHERE root_id = %s", (knowledge.root_id,))


def test_promote_to_confirmed_raises_for_unknown_id(postgres_dsn):
    from app.knowledge.knowledge_model import KnowledgeNotFoundError

    with pytest.raises(KnowledgeNotFoundError):
        promote_to_confirmed(uuid.uuid4())


def test_promote_to_confirmed_does_not_change_status_when_not_eligible(
    postgres_dsn, provisional_knowledge
):
    from app.knowledge.knowledge_model import get_knowledge

    with pytest.raises(KnowledgePromotionNotEligibleError):
        promote_to_confirmed(provisional_knowledge.id)

    unchanged = get_knowledge(provisional_knowledge.id)
    assert unchanged.status == KnowledgeStatus.PROVISIONAL
