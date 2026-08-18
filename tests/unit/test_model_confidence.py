"""Testes unitários da confiança do modelo LOW/MEDIUM/HIGH (TASK-031)."""

import pytest

from app.confidence.model_confidence import (
    CONFIDENCE_ORDER,
    NoRespondStepError,
    get_model_confidence,
    is_at_least,
)
from app.llm.protocol import Action, Confidence, ModelStep
from app.orchestrator.execution import Execution


def _use_tool_step(execution_id: str) -> ModelStep:
    return ModelStep(
        execution_id=execution_id,
        action=Action.USE_TOOL,
        confidence=Confidence.LOW,
        reason="preciso pesquisar",
        tool="WEB_SEARCH",
        parameters={},
    )


def _respond_step(execution_id: str, confidence: Confidence) -> ModelStep:
    return ModelStep(
        execution_id=execution_id,
        action=Action.RESPOND,
        confidence=confidence,
        reason="resposta pronta",
    )


def test_confidence_order_is_low_medium_high():
    assert CONFIDENCE_ORDER[Confidence.LOW] < CONFIDENCE_ORDER[Confidence.MEDIUM]
    assert CONFIDENCE_ORDER[Confidence.MEDIUM] < CONFIDENCE_ORDER[Confidence.HIGH]
    assert len(CONFIDENCE_ORDER) == 3


@pytest.mark.parametrize(
    "confidence,minimum,expected",
    [
        (Confidence.HIGH, Confidence.LOW, True),
        (Confidence.HIGH, Confidence.HIGH, True),
        (Confidence.LOW, Confidence.HIGH, False),
        (Confidence.MEDIUM, Confidence.MEDIUM, True),
        (Confidence.MEDIUM, Confidence.HIGH, False),
        (Confidence.LOW, Confidence.LOW, True),
    ],
)
def test_is_at_least(confidence, minimum, expected):
    assert is_at_least(confidence, minimum) is expected


def test_get_model_confidence_from_respond_step():
    execution = Execution.new(origin="chat")
    execution.start()
    execution.add_step(_respond_step(execution.execution_id, Confidence.HIGH))

    assert get_model_confidence(execution) == Confidence.HIGH


def test_get_model_confidence_ignores_earlier_use_tool_steps():
    execution = Execution.new(origin="chat")
    execution.start()
    execution.add_step(_use_tool_step(execution.execution_id))
    execution.set_last_observation("resultado")
    execution.add_step(_respond_step(execution.execution_id, Confidence.MEDIUM))

    assert get_model_confidence(execution) == Confidence.MEDIUM


def test_get_model_confidence_raises_without_respond_step():
    execution = Execution.new(origin="chat")
    execution.start()
    execution.add_step(_use_tool_step(execution.execution_id))

    with pytest.raises(NoRespondStepError):
        get_model_confidence(execution)


def test_get_model_confidence_raises_for_empty_execution():
    execution = Execution.new(origin="chat")

    with pytest.raises(NoRespondStepError):
        get_model_confidence(execution)
