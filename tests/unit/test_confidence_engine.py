"""Testes unitários do Confidence Engine do orquestrador (TASK-033)."""

import pytest

from app.confidence.confidence_engine import (
    EvidenceStrength,
    calculate_final_confidence,
    calculate_final_confidence_for_execution,
)
from app.confidence.model_confidence import NoRespondStepError
from app.llm.protocol import Action, Confidence, ModelStep
from app.orchestrator.execution import Execution


def test_evidence_strength_has_exactly_three_values():
    assert {e.value for e in EvidenceStrength} == {"NONE", "WEAK", "STRONG"}


@pytest.mark.parametrize(
    "model_confidence,evidence,expected",
    [
        # HIGH é rebaixado quando a evidência não é forte.
        (Confidence.HIGH, EvidenceStrength.WEAK, Confidence.MEDIUM),
        (Confidence.HIGH, EvidenceStrength.NONE, Confidence.MEDIUM),
        (Confidence.HIGH, EvidenceStrength.STRONG, Confidence.HIGH),
        # MEDIUM é elevado só com evidência forte.
        (Confidence.MEDIUM, EvidenceStrength.STRONG, Confidence.HIGH),
        (Confidence.MEDIUM, EvidenceStrength.WEAK, Confidence.MEDIUM),
        (Confidence.MEDIUM, EvidenceStrength.NONE, Confidence.MEDIUM),
        # LOW nunca é elevado por evidência (seção 13.3 só menciona MEDIUM).
        (Confidence.LOW, EvidenceStrength.STRONG, Confidence.LOW),
        (Confidence.LOW, EvidenceStrength.WEAK, Confidence.LOW),
        (Confidence.LOW, EvidenceStrength.NONE, Confidence.LOW),
    ],
)
def test_calculate_final_confidence(model_confidence, evidence, expected):
    assert calculate_final_confidence(model_confidence, evidence) == expected


def test_calculate_final_confidence_for_execution_reads_respond_step():
    execution = Execution.new(origin="chat")
    execution.start()
    execution.add_step(
        ModelStep(
            execution_id=execution.execution_id,
            action=Action.RESPOND,
            confidence=Confidence.HIGH,
            reason="resposta pronta",
        )
    )

    final = calculate_final_confidence_for_execution(execution, EvidenceStrength.WEAK)

    assert final == Confidence.MEDIUM


def test_calculate_final_confidence_for_execution_propagates_no_respond_error():
    execution = Execution.new(origin="chat")
    execution.start()
    execution.add_step(
        ModelStep(
            execution_id=execution.execution_id,
            action=Action.USE_TOOL,
            confidence=Confidence.LOW,
            reason="preciso pesquisar",
            tool="WEB_SEARCH",
            parameters={},
        )
    )

    with pytest.raises(NoRespondStepError):
        calculate_final_confidence_for_execution(execution, EvidenceStrength.STRONG)
