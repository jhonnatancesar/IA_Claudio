"""Testes unitários da Memory Tool (TASK-046) — só validação de parâmetros,
sem tocar o banco (dispatch real é teste de integração, já que persiste
dados)."""

import pytest

from app.llm.protocol import Action, Confidence, ModelStep
from app.tools.memory_tool import (
    MissingToolParameterError,
    UnknownMemoryOperationError,
    execute_memory_tool,
)


def _step(parameters: dict) -> ModelStep:
    return ModelStep(
        execution_id="11111111-1111-1111-1111-111111111111",
        action=Action.USE_TOOL,
        confidence=Confidence.MEDIUM,
        reason="usar memória",
        tool="MEMORY",
        parameters=parameters,
    )


def test_missing_operation_raises():
    with pytest.raises(MissingToolParameterError):
        execute_memory_tool(_step({}))


def test_unknown_operation_raises():
    with pytest.raises(UnknownMemoryOperationError):
        execute_memory_tool(_step({"operation": "DELETE"}))


def test_save_missing_owner_type_raises():
    with pytest.raises(MissingToolParameterError):
        execute_memory_tool(_step({"operation": "SAVE", "owner_id": "x", "content": "y"}))


def test_save_missing_owner_id_raises():
    with pytest.raises(MissingToolParameterError):
        execute_memory_tool(
            _step({"operation": "SAVE", "owner_type": "USER", "content": "y"})
        )


def test_save_missing_content_raises():
    with pytest.raises(MissingToolParameterError):
        execute_memory_tool(
            _step({"operation": "SAVE", "owner_type": "USER", "owner_id": "x"})
        )


def test_list_missing_owner_type_raises():
    with pytest.raises(MissingToolParameterError):
        execute_memory_tool(_step({"operation": "LIST", "owner_id": "x"}))


def test_list_missing_owner_id_raises():
    with pytest.raises(MissingToolParameterError):
        execute_memory_tool(_step({"operation": "LIST", "owner_type": "USER"}))
