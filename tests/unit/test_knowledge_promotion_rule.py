"""Testes unitários da regra de promoção para CONFIRMED (TASK-057) — só
`is_eligible_for_confirmation`, função pura, sem tocar o banco."""

from app.knowledge.knowledge_model import Knowledge, KnowledgeScope, KnowledgeStatus
from app.knowledge.promotion_rule import is_eligible_for_confirmation
from app.llm.protocol import Confidence


def _knowledge(status: KnowledgeStatus, confidence: Confidence | None) -> Knowledge:
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
        confidence=confidence,
        volatility=None,
    )


def test_provisional_high_confidence_with_evidence_is_eligible():
    knowledge = _knowledge(KnowledgeStatus.PROVISIONAL, Confidence.HIGH)

    assert is_eligible_for_confirmation(knowledge, evidence_count=1) is True


def test_provisional_high_confidence_without_evidence_is_not_eligible():
    knowledge = _knowledge(KnowledgeStatus.PROVISIONAL, Confidence.HIGH)

    assert is_eligible_for_confirmation(knowledge, evidence_count=0) is False


def test_provisional_medium_confidence_is_not_eligible():
    knowledge = _knowledge(KnowledgeStatus.PROVISIONAL, Confidence.MEDIUM)

    assert is_eligible_for_confirmation(knowledge, evidence_count=5) is False


def test_provisional_no_confidence_is_not_eligible():
    knowledge = _knowledge(KnowledgeStatus.PROVISIONAL, None)

    assert is_eligible_for_confirmation(knowledge, evidence_count=5) is False


def test_raw_status_is_not_eligible_even_with_high_confidence_and_evidence():
    knowledge = _knowledge(KnowledgeStatus.RAW, Confidence.HIGH)

    assert is_eligible_for_confirmation(knowledge, evidence_count=5) is False


def test_confirmed_status_is_not_eligible_again():
    knowledge = _knowledge(KnowledgeStatus.CONFIRMED, Confidence.HIGH)

    assert is_eligible_for_confirmation(knowledge, evidence_count=5) is False
