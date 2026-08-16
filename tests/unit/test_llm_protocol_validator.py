"""Testes unitários da validação semântica do protocolo (TASK-017)."""

import json

import pytest

from app.errors.response import ClaudiaoError
from app.llm.protocol_validator import INVALID_MODEL_STEP, validate_step

_VALID_STEP = {
    "execution_id": "12345678-1234-5678-1234-567812345678",
    "action": "RESPOND",
    "confidence": "HIGH",
    "reason": "resposta pronta",
}


def test_validate_step_accepts_valid_json():
    step = validate_step(json.dumps(_VALID_STEP))

    assert step.execution_id == _VALID_STEP["execution_id"]
    assert step.reason == "resposta pronta"


def test_validate_step_raises_claudiao_error_for_malformed_json():
    with pytest.raises(ClaudiaoError) as exc_info:
        validate_step("{isso nao e json valido")

    assert exc_info.value.definition is INVALID_MODEL_STEP
    assert exc_info.value.definition.code == 4001
    assert exc_info.value.definition.http_status == 502


def test_validate_step_raises_claudiao_error_for_missing_field():
    payload = dict(_VALID_STEP)
    del payload["reason"]

    with pytest.raises(ClaudiaoError) as exc_info:
        validate_step(json.dumps(payload))

    assert exc_info.value.definition is INVALID_MODEL_STEP


def test_validate_step_raises_claudiao_error_for_invalid_action():
    payload = dict(_VALID_STEP, action="ACAO_INVENTADA")

    with pytest.raises(ClaudiaoError):
        validate_step(json.dumps(payload))


def test_validate_step_rejects_non_uuid_execution_id():
    payload = dict(_VALID_STEP, execution_id="nao-e-um-uuid")

    with pytest.raises(ClaudiaoError) as exc_info:
        validate_step(json.dumps(payload))

    assert exc_info.value.definition is INVALID_MODEL_STEP
    assert "execution_id" in exc_info.value.details["reason"]


def test_validate_step_rejects_empty_reason():
    payload = dict(_VALID_STEP, reason="   ")

    with pytest.raises(ClaudiaoError) as exc_info:
        validate_step(json.dumps(payload))

    assert "reason" in exc_info.value.details["reason"]


def test_validate_step_error_details_carry_human_readable_reason():
    with pytest.raises(ClaudiaoError) as exc_info:
        validate_step("não é json")

    assert isinstance(exc_info.value.details, dict)
    assert "reason" in exc_info.value.details
    assert exc_info.value.details["reason"]  # não vazio


def test_validate_step_accepts_use_tool_with_valid_uuid():
    payload = {
        "execution_id": "12345678-1234-5678-1234-567812345678",
        "action": "USE_TOOL",
        "tool": "WEB_SEARCH",
        "confidence": "LOW",
        "reason": "preciso pesquisar",
        "parameters": {"query": "algo"},
    }

    step = validate_step(json.dumps(payload))

    assert step.tool == "WEB_SEARCH"
