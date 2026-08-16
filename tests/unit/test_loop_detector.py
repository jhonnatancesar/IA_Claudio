"""Testes unitários da detecção de loop (TASK-029)."""

import pytest

from app.llm.protocol import Action, Confidence, ModelStep
from app.orchestrator.execution import Execution
from app.orchestrator.loop_detector import detect_loop


def _use_tool_step(execution_id: str, tool: str = "WEB_SEARCH", **params) -> ModelStep:
    return ModelStep(
        execution_id=execution_id,
        action=Action.USE_TOOL,
        confidence=Confidence.LOW,
        reason="preciso pesquisar",
        tool=tool,
        parameters=params,
    )


def _respond_step(execution_id: str) -> ModelStep:
    return ModelStep(
        execution_id=execution_id,
        action=Action.RESPOND,
        confidence=Confidence.HIGH,
        reason="pronto",
    )


def _execution_with_steps(*steps: ModelStep) -> Execution:
    execution = Execution.new(origin="chat")
    execution.start()
    for step in steps:
        execution.add_step(step)
        if step.action != Action.RESPOND:
            execution.set_last_observation("resultado qualquer")
    return execution


def test_no_loop_with_fewer_steps_than_threshold():
    execution = _execution_with_steps(
        _use_tool_step("x", query="a"), _use_tool_step("x", query="a")
    )

    assert detect_loop(execution, threshold=3) is False


def test_loop_detected_with_identical_repeated_steps():
    execution = _execution_with_steps(
        _use_tool_step("x", query="a"),
        _use_tool_step("x", query="a"),
        _use_tool_step("x", query="a"),
    )

    assert detect_loop(execution, threshold=3) is True


def test_no_loop_when_parameters_differ_between_calls():
    execution = _execution_with_steps(
        _use_tool_step("x", query="a"),
        _use_tool_step("x", query="b"),
        _use_tool_step("x", query="c"),
    )

    assert detect_loop(execution, threshold=3) is False


def test_no_loop_when_tool_differs_between_calls():
    execution = _execution_with_steps(
        _use_tool_step("x", tool="WEB_SEARCH", query="a"),
        _use_tool_step("x", tool="MEMORY_TOOL", query="a"),
        _use_tool_step("x", tool="WEB_SEARCH", query="a"),
    )

    assert detect_loop(execution, threshold=3) is False


def test_no_loop_when_respond_is_among_last_steps():
    execution = _execution_with_steps(
        _use_tool_step("x", query="a"),
        _use_tool_step("x", query="a"),
        _respond_step("x"),
    )

    assert detect_loop(execution, threshold=3) is False


def test_loop_uses_only_the_last_threshold_steps():
    execution = _execution_with_steps(
        _use_tool_step("x", query="different"),
        _use_tool_step("x", query="a"),
        _use_tool_step("x", query="a"),
        _use_tool_step("x", query="a"),
    )

    assert detect_loop(execution, threshold=3) is True


def test_detect_loop_rejects_threshold_below_two():
    execution = _execution_with_steps(_use_tool_step("x"))

    with pytest.raises(ValueError):
        detect_loop(execution, threshold=1)


def test_custom_threshold_of_two():
    execution = _execution_with_steps(
        _use_tool_step("x", query="a"), _use_tool_step("x", query="a")
    )

    assert detect_loop(execution, threshold=2) is True
