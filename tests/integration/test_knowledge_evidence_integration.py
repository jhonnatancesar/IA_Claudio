"""Teste de integração: evidências/confiança/volatilidade de conhecimento
(TASK-056) contra o PostgreSQL local. Usa a fixture `postgres_dsn`
(tests/integration/conftest.py) — pula automaticamente se o banco não
estiver disponível.
"""

import uuid

import psycopg
import pytest

from app.confidence.volatility import Volatility
from app.knowledge.knowledge_model import (
    KnowledgeNotFoundError,
    add_evidence,
    list_evidence,
    save_knowledge,
    set_knowledge_confidence,
    set_knowledge_volatility,
)
from app.llm.protocol import Confidence


@pytest.fixture
def created_knowledge(postgres_dsn):
    knowledge = save_knowledge(f"fato de teste {uuid.uuid4().hex[:12]}")
    yield knowledge
    with psycopg.connect(postgres_dsn) as conn:
        conn.execute("DELETE FROM knowledge_evidence WHERE knowledge_id = %s", (knowledge.id,))
        conn.execute("DELETE FROM knowledge WHERE root_id = %s", (knowledge.root_id,))


def test_new_knowledge_has_no_confidence_or_volatility(postgres_dsn, created_knowledge):
    assert created_knowledge.confidence is None
    assert created_knowledge.volatility is None


def test_set_knowledge_confidence(postgres_dsn, created_knowledge):
    updated = set_knowledge_confidence(created_knowledge.id, Confidence.HIGH)

    assert updated.confidence == Confidence.HIGH


def test_set_knowledge_volatility(postgres_dsn, created_knowledge):
    updated = set_knowledge_volatility(created_knowledge.id, Volatility.VOLATILE)

    assert updated.volatility == Volatility.VOLATILE


def test_set_knowledge_confidence_raises_for_unknown_id(postgres_dsn):
    with pytest.raises(KnowledgeNotFoundError):
        set_knowledge_confidence(uuid.uuid4(), Confidence.LOW)


def test_set_knowledge_volatility_raises_for_unknown_id(postgres_dsn):
    with pytest.raises(KnowledgeNotFoundError):
        set_knowledge_volatility(uuid.uuid4(), Volatility.NON_VOLATILE)


def test_add_and_list_evidence(postgres_dsn, created_knowledge):
    add_evidence(created_knowledge.id, "documentação oficial do fabricante")
    add_evidence(created_knowledge.id, "confirmado por segunda fonte independente")

    evidence = list_evidence(created_knowledge.id)

    assert [e.description for e in evidence] == [
        "documentação oficial do fabricante",
        "confirmado por segunda fonte independente",
    ]


def test_list_evidence_empty_when_none_added(postgres_dsn, created_knowledge):
    assert list_evidence(created_knowledge.id) == []


def test_add_evidence_raises_for_unknown_knowledge_id(postgres_dsn):
    with pytest.raises(KnowledgeNotFoundError):
        add_evidence(uuid.uuid4(), "evidência qualquer")
