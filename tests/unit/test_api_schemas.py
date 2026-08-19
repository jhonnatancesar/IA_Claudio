"""Testes unitários de validação de payload (TASK-068) — só o schema
Pydantic, sem tocar o banco nem a API HTTP."""

import pytest
from pydantic import ValidationError

from app.api.schemas import ExecutionRequest

_VALID_PAYLOAD = {
    "objective": "buscar o clima de hoje",
    "usage_type": "chat",
    "web_search_allowed": True,
    "timeout_seconds": 30,
}


def test_valid_payload_is_accepted():
    request = ExecutionRequest(**_VALID_PAYLOAD)

    assert request.objective == "buscar o clima de hoje"
    assert request.context is None
    assert request.max_steps is None


@pytest.mark.parametrize(
    "missing_field", ["objective", "usage_type", "web_search_allowed", "timeout_seconds"]
)
def test_missing_required_field_is_rejected(missing_field):
    payload = {k: v for k, v in _VALID_PAYLOAD.items() if k != missing_field}

    with pytest.raises(ValidationError):
        ExecutionRequest(**payload)


def test_empty_objective_is_rejected():
    with pytest.raises(ValidationError):
        ExecutionRequest(**{**_VALID_PAYLOAD, "objective": ""})


def test_non_positive_timeout_is_rejected():
    with pytest.raises(ValidationError):
        ExecutionRequest(**{**_VALID_PAYLOAD, "timeout_seconds": 0})


def test_non_positive_max_steps_is_rejected():
    with pytest.raises(ValidationError):
        ExecutionRequest(**{**_VALID_PAYLOAD, "max_steps": 0})


def test_wrong_type_for_web_search_allowed_is_rejected():
    with pytest.raises(ValidationError):
        ExecutionRequest(**{**_VALID_PAYLOAD, "web_search_allowed": ["não", "é", "bool"]})


def test_optional_fields_accept_explicit_values():
    request = ExecutionRequest(**_VALID_PAYLOAD, context={"lang": "pt-BR"}, max_steps=5)

    assert request.context == {"lang": "pt-BR"}
    assert request.max_steps == 5
