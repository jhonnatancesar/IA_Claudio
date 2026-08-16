"""Testes unitários de observações por etapa em Execution (TASK-026)."""

import pytest

from app.llm.protocol import Action, Confidence, ModelStep
from app.orchestrator.execution import Execution, InvalidExecutionStateError


def _step(execution_id: str, reason: str = "etapa") -> ModelStep:
    return ModelStep(
        execution_id=execution_id,
        action=Action.USE_TOOL,
        confidence=Confidence.LOW,
        reason=reason,
        tool="WEB_SEARCH",
        parameters={},
    )


def test_add_step_appends_none_observation():
    execution = Execution.new(origin="chat")
    execution.start()

    execution.add_step(_step(execution.execution_id))

    assert execution.observations == [None]


def test_set_last_observation_sets_value_for_last_step():
    execution = Execution.new(origin="chat")
    execution.start()
    execution.add_step(_step(execution.execution_id))

    execution.set_last_observation("resultado encontrado")

    assert execution.observations == ["resultado encontrado"]


def test_set_last_observation_raises_when_no_steps():
    execution = Execution.new(origin="chat")
    execution.start()

    with pytest.raises(InvalidExecutionStateError):
        execution.set_last_observation("algo")


def test_set_last_observation_raises_when_already_set():
    execution = Execution.new(origin="chat")
    execution.start()
    execution.add_step(_step(execution.execution_id))
    execution.set_last_observation("primeiro resultado")

    with pytest.raises(InvalidExecutionStateError):
        execution.set_last_observation("segundo resultado")


def test_observations_align_with_multiple_steps():
    execution = Execution.new(origin="chat")
    execution.start()
    execution.add_step(_step(execution.execution_id, "primeira"))
    execution.set_last_observation("resultado 1")
    execution.add_step(_step(execution.execution_id, "segunda"))
    # segunda etapa fica sem observação ainda

    assert execution.observations == ["resultado 1", None]
    assert len(execution.observations) == execution.step_count
