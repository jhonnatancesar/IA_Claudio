"""Testes unitários da validação de plano do orquestrador (TASK-025)."""

import pytest

from app.errors.response import ClaudiaoError
from app.llm.protocol import Action, Confidence, ModelStep
from app.orchestrator.execution import Execution
from app.orchestrator.plan_validator import (
    PLAN_EXECUTION_ID_MISMATCH,
    PLAN_TOOL_NOT_AUTHORIZED,
    validate_plan,
)
from app.policies.execution_policy import ExecutionPolicy


def _respond_step(execution_id: str) -> ModelStep:
    return ModelStep(
        execution_id=execution_id,
        action=Action.RESPOND,
        confidence=Confidence.HIGH,
        reason="resposta pronta",
    )


def _use_tool_step(execution_id: str, tool: str = "WEB_SEARCH") -> ModelStep:
    return ModelStep(
        execution_id=execution_id,
        action=Action.USE_TOOL,
        confidence=Confidence.LOW,
        reason="preciso de ajuda externa",
        tool=tool,
        parameters={"query": "algo"},
    )


def test_validate_plan_accepts_matching_respond_step():
    execution = Execution.new(origin="chat")
    step = _respond_step(execution.execution_id)

    validate_plan(step, execution, ExecutionPolicy.for_chat())  # não levanta


def test_validate_plan_rejects_execution_id_mismatch():
    execution = Execution.new(origin="chat")
    step = _respond_step("outro-execution-id-completamente-diferente")

    with pytest.raises(ClaudiaoError) as exc_info:
        validate_plan(step, execution, ExecutionPolicy.for_chat())

    assert exc_info.value.definition is PLAN_EXECUTION_ID_MISMATCH
    assert exc_info.value.definition.code == 4002


def test_validate_plan_rejects_web_search_when_not_authorized():
    execution = Execution.new(origin="chat")
    step = _use_tool_step(execution.execution_id, tool="WEB_SEARCH")
    policy = ExecutionPolicy.for_chat(web_search_allowed=False)

    with pytest.raises(ClaudiaoError) as exc_info:
        validate_plan(step, execution, policy)

    assert exc_info.value.definition is PLAN_TOOL_NOT_AUTHORIZED
    assert exc_info.value.definition.code == 4003
    assert exc_info.value.details == {"tool": "WEB_SEARCH"}


def test_validate_plan_accepts_web_search_when_authorized():
    execution = Execution.new(origin="chat")
    step = _use_tool_step(execution.execution_id, tool="WEB_SEARCH")
    policy = ExecutionPolicy.for_chat(web_search_allowed=True)

    validate_plan(step, execution, policy)  # não levanta


def test_validate_plan_accepts_non_search_tool_regardless_of_search_policy():
    execution = Execution.new(origin="chat")
    step = _use_tool_step(execution.execution_id, tool="MEMORY_TOOL")
    policy = ExecutionPolicy.for_chat(web_search_allowed=False)

    validate_plan(step, execution, policy)  # não levanta — só WEB_SEARCH é checado
