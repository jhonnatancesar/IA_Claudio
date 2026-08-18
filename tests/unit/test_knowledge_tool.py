"""Testes unitários da Knowledge Tool (TASK-053) — só validação de
parâmetros, sem tocar o banco (dispatch real é teste de integração, já
que persiste dados)."""

import pytest

from app.llm.protocol import Action, Confidence, ModelStep
from app.tools.knowledge_tool import (
    InvalidKnowledgeStatusParameterError,
    MissingToolParameterError,
    UnknownKnowledgeOperationError,
    execute_knowledge_tool,
)


def _step(parameters: dict) -> ModelStep:
    return ModelStep(
        execution_id="11111111-1111-1111-1111-111111111111",
        action=Action.USE_TOOL,
        confidence=Confidence.MEDIUM,
        reason="usar conhecimento",
        tool="KNOWLEDGE",
        parameters=parameters,
    )


def test_missing_operation_raises():
    with pytest.raises(MissingToolParameterError):
        execute_knowledge_tool(_step({}))


def test_unknown_operation_raises():
    with pytest.raises(UnknownKnowledgeOperationError):
        execute_knowledge_tool(_step({"operation": "DELETE"}))


def test_save_missing_content_raises():
    with pytest.raises(MissingToolParameterError):
        execute_knowledge_tool(_step({"operation": "SAVE"}))


def test_get_missing_knowledge_id_raises():
    with pytest.raises(MissingToolParameterError):
        execute_knowledge_tool(_step({"operation": "GET"}))


def test_advance_missing_knowledge_id_raises():
    with pytest.raises(MissingToolParameterError):
        execute_knowledge_tool(_step({"operation": "ADVANCE", "new_status": "PROVISIONAL"}))


def test_advance_missing_new_status_raises():
    with pytest.raises(MissingToolParameterError):
        execute_knowledge_tool(
            _step({"operation": "ADVANCE", "knowledge_id": "11111111-1111-1111-1111-111111111111"})
        )


def test_advance_invalid_new_status_raises():
    with pytest.raises(InvalidKnowledgeStatusParameterError):
        execute_knowledge_tool(
            _step(
                {
                    "operation": "ADVANCE",
                    "knowledge_id": "11111111-1111-1111-1111-111111111111",
                    "new_status": "APPROVED",
                }
            )
        )
