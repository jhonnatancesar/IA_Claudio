"""Testes unitários da Knowledge Tool (TASK-053) — só validação de
parâmetros, sem tocar o banco (dispatch real é teste de integração, já
que persiste dados)."""

import pytest

from app.llm.protocol import Action, Confidence, ModelStep
from app.tools.knowledge_tool import (
    InvalidConfidenceParameterError,
    InvalidKnowledgeScopeParameterError,
    InvalidKnowledgeStatusParameterError,
    InvalidVolatilityParameterError,
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


def test_new_version_missing_knowledge_id_raises():
    with pytest.raises(MissingToolParameterError):
        execute_knowledge_tool(
            _step({"operation": "NEW_VERSION", "new_content": "x", "reason": "y"})
        )


def test_new_version_missing_new_content_raises():
    with pytest.raises(MissingToolParameterError):
        execute_knowledge_tool(
            _step(
                {
                    "operation": "NEW_VERSION",
                    "knowledge_id": "11111111-1111-1111-1111-111111111111",
                    "reason": "y",
                }
            )
        )


def test_save_invalid_scope_type_raises():
    with pytest.raises(InvalidKnowledgeScopeParameterError):
        execute_knowledge_tool(
            _step({"operation": "SAVE", "content": "x", "scope_type": "TEAM"})
        )


def test_list_scope_missing_scope_type_raises():
    with pytest.raises(MissingToolParameterError):
        execute_knowledge_tool(_step({"operation": "LIST_SCOPE"}))


def test_list_scope_invalid_scope_type_raises():
    with pytest.raises(InvalidKnowledgeScopeParameterError):
        execute_knowledge_tool(_step({"operation": "LIST_SCOPE", "scope_type": "TEAM"}))


def test_set_confidence_missing_knowledge_id_raises():
    with pytest.raises(MissingToolParameterError):
        execute_knowledge_tool(_step({"operation": "SET_CONFIDENCE", "confidence": "HIGH"}))


def test_set_confidence_missing_confidence_raises():
    with pytest.raises(MissingToolParameterError):
        execute_knowledge_tool(
            _step(
                {
                    "operation": "SET_CONFIDENCE",
                    "knowledge_id": "11111111-1111-1111-1111-111111111111",
                }
            )
        )


def test_set_confidence_invalid_confidence_raises():
    with pytest.raises(InvalidConfidenceParameterError):
        execute_knowledge_tool(
            _step(
                {
                    "operation": "SET_CONFIDENCE",
                    "knowledge_id": "11111111-1111-1111-1111-111111111111",
                    "confidence": "MAXIMUM",
                }
            )
        )


def test_set_volatility_missing_knowledge_id_raises():
    with pytest.raises(MissingToolParameterError):
        execute_knowledge_tool(_step({"operation": "SET_VOLATILITY", "volatility": "VOLATILE"}))


def test_set_volatility_invalid_volatility_raises():
    with pytest.raises(InvalidVolatilityParameterError):
        execute_knowledge_tool(
            _step(
                {
                    "operation": "SET_VOLATILITY",
                    "knowledge_id": "11111111-1111-1111-1111-111111111111",
                    "volatility": "SOMETIMES",
                }
            )
        )


def test_add_evidence_missing_knowledge_id_raises():
    with pytest.raises(MissingToolParameterError):
        execute_knowledge_tool(_step({"operation": "ADD_EVIDENCE", "description": "x"}))


def test_add_evidence_missing_description_raises():
    with pytest.raises(MissingToolParameterError):
        execute_knowledge_tool(
            _step(
                {
                    "operation": "ADD_EVIDENCE",
                    "knowledge_id": "11111111-1111-1111-1111-111111111111",
                }
            )
        )


def test_list_evidence_missing_knowledge_id_raises():
    with pytest.raises(MissingToolParameterError):
        execute_knowledge_tool(_step({"operation": "LIST_EVIDENCE"}))


def test_new_version_missing_reason_raises():
    with pytest.raises(MissingToolParameterError):
        execute_knowledge_tool(
            _step(
                {
                    "operation": "NEW_VERSION",
                    "knowledge_id": "11111111-1111-1111-1111-111111111111",
                    "new_content": "x",
                }
            )
        )
