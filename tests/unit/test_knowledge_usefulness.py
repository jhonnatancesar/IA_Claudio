"""Testes unitários da avaliação de utilidade pelo orquestrador
(TASK-058) — função pura, sem tocar o banco."""

from app.knowledge.knowledge_model import Knowledge, KnowledgeScope, KnowledgeStatus
from app.knowledge.usefulness import is_useful_for_orchestrator


def _knowledge(status: KnowledgeStatus) -> Knowledge:
    return Knowledge(
        id="00000000-0000-0000-0000-000000000000",
        status=status,
        content="fato de teste",
        created_at=None,
        root_id="00000000-0000-0000-0000-000000000000",
        version=1,
        is_current=True,
        previous_version_id=None,
        change_reason=None,
        scope_type=KnowledgeScope.GLOBAL,
        scope_id=None,
        confidence=None,
        volatility=None,
    )


def test_confirmed_and_relevant_is_useful():
    knowledge = _knowledge(KnowledgeStatus.CONFIRMED)

    assert is_useful_for_orchestrator(knowledge, is_relevant_to_objective=True) is True


def test_confirmed_but_not_relevant_is_not_useful():
    knowledge = _knowledge(KnowledgeStatus.CONFIRMED)

    assert is_useful_for_orchestrator(knowledge, is_relevant_to_objective=False) is False


def test_provisional_and_relevant_is_not_useful():
    knowledge = _knowledge(KnowledgeStatus.PROVISIONAL)

    assert is_useful_for_orchestrator(knowledge, is_relevant_to_objective=True) is False


def test_raw_and_relevant_is_not_useful():
    knowledge = _knowledge(KnowledgeStatus.RAW)

    assert is_useful_for_orchestrator(knowledge, is_relevant_to_objective=True) is False


def test_raw_and_not_relevant_is_not_useful():
    knowledge = _knowledge(KnowledgeStatus.RAW)

    assert is_useful_for_orchestrator(knowledge, is_relevant_to_objective=False) is False
