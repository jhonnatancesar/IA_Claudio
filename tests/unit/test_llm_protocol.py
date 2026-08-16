"""Testes unitários do protocolo JSON modelo ↔ orquestrador (TASK-016)."""

import pytest

from app.llm.protocol import Action, Confidence, ModelStep, ProtocolDecodeError

_SPEC_EXAMPLE = {
    "execution_id": "uuid",
    "action": "USE_TOOL",
    "tool": "WEB_SEARCH",
    "confidence": "LOW",
    "reason": "Informação atual necessária",
    "parameters": {"query": "..."},
}


def test_from_dict_matches_spec_example():
    step = ModelStep.from_dict(_SPEC_EXAMPLE)

    assert step.execution_id == "uuid"
    assert step.action == Action.USE_TOOL
    assert step.tool == "WEB_SEARCH"
    assert step.confidence == Confidence.LOW
    assert step.reason == "Informação atual necessária"
    assert step.parameters == {"query": "..."}


def test_to_dict_roundtrips_spec_example():
    step = ModelStep.from_dict(_SPEC_EXAMPLE)

    assert step.to_dict() == _SPEC_EXAMPLE


def test_from_json_roundtrips_to_json():
    step = ModelStep.from_dict(_SPEC_EXAMPLE)

    reloaded = ModelStep.from_json(step.to_json())

    assert reloaded == step


def test_respond_action_without_tool_is_valid():
    step = ModelStep.from_dict(
        {
            "execution_id": "uuid-2",
            "action": "RESPOND",
            "confidence": "HIGH",
            "reason": "Já sei a resposta",
        }
    )

    assert step.action == Action.RESPOND
    assert step.tool is None
    assert step.parameters == {}


def test_to_dict_omits_tool_and_parameters_when_absent():
    step = ModelStep.from_dict(
        {
            "execution_id": "uuid-3",
            "action": "RESPOND",
            "confidence": "MEDIUM",
            "reason": "resposta parcial",
        }
    )

    data = step.to_dict()

    assert "tool" not in data
    assert "parameters" not in data


@pytest.mark.parametrize("missing_field", ["execution_id", "action", "confidence", "reason"])
def test_from_dict_rejects_missing_required_field(missing_field):
    payload = dict(_SPEC_EXAMPLE)
    del payload[missing_field]

    with pytest.raises(ProtocolDecodeError):
        ModelStep.from_dict(payload)


def test_from_dict_rejects_invalid_action():
    payload = dict(_SPEC_EXAMPLE, action="FAZER_MAGICA")

    with pytest.raises(ProtocolDecodeError):
        ModelStep.from_dict(payload)


def test_from_dict_rejects_invalid_confidence():
    payload = dict(_SPEC_EXAMPLE, confidence="CERTEZA_ABSOLUTA")

    with pytest.raises(ProtocolDecodeError):
        ModelStep.from_dict(payload)


def test_from_dict_rejects_use_tool_without_tool_field():
    payload = {
        "execution_id": "uuid-4",
        "action": "USE_TOOL",
        "confidence": "LOW",
        "reason": "preciso pesquisar",
    }

    with pytest.raises(ProtocolDecodeError):
        ModelStep.from_dict(payload)


def test_from_dict_rejects_non_dict_input():
    with pytest.raises(ProtocolDecodeError):
        ModelStep.from_dict(["isso", "nao", "e", "um", "objeto"])


def test_from_json_rejects_malformed_json():
    with pytest.raises(ProtocolDecodeError):
        ModelStep.from_json("{isso nao e json valido")


def test_from_json_rejects_json_array_at_top_level():
    with pytest.raises(ProtocolDecodeError):
        ModelStep.from_json("[1, 2, 3]")


def test_from_dict_rejects_non_dict_parameters():
    """Regressão (TASK-017): antes do fix, `parameters` não-dict escapava
    como ValueError/TypeError genérico em vez de ProtocolDecodeError."""
    payload = dict(_SPEC_EXAMPLE, parameters="isso não é um objeto")

    with pytest.raises(ProtocolDecodeError):
        ModelStep.from_dict(payload)


def test_from_dict_rejects_list_as_parameters():
    payload = dict(_SPEC_EXAMPLE, parameters=["a", "b"])

    with pytest.raises(ProtocolDecodeError):
        ModelStep.from_dict(payload)


def test_to_json_does_not_escape_non_ascii_characters():
    """Regressão (TASK-019): sem ensure_ascii=False, acentos em `reason`
    viravam \\uXXXX — o protocolo é PT-BR, então o JSON deve ficar legível."""
    step = ModelStep.from_dict(_SPEC_EXAMPLE)

    raw = step.to_json()

    assert "Informação atual necessária" in raw
    assert "\\u" not in raw
