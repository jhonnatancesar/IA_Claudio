"""Testes unitários da composição dinâmica de prompt/contexto (TASK-019)."""

import pytest

from app.llm.prompt import BASE_PROMPT
from app.llm.prompt_composer import StepRecord, compose_prompt
from app.llm.protocol import Action, Confidence, ModelStep


def test_compose_prompt_includes_base_prompt():
    prompt = compose_prompt("exec-1", "responda o que é o Claudião")

    assert BASE_PROMPT in prompt


def test_compose_prompt_includes_execution_id_and_objective():
    prompt = compose_prompt("exec-1", "responda o que é o Claudião")

    assert "exec-1" in prompt
    assert "responda o que é o Claudião" in prompt


def test_compose_prompt_strips_objective_whitespace():
    prompt = compose_prompt("exec-1", "   pergunta com espaços   ")

    assert "pergunta com espaços" in prompt
    assert "   pergunta com espaços   " not in prompt


def test_compose_prompt_rejects_empty_objective():
    with pytest.raises(ValueError):
        compose_prompt("exec-1", "")


def test_compose_prompt_rejects_whitespace_only_objective():
    with pytest.raises(ValueError):
        compose_prompt("exec-1", "   ")


def test_compose_prompt_without_history_omits_history_section():
    prompt = compose_prompt("exec-1", "pergunta")

    assert "Etapas já executadas" not in prompt


def test_compose_prompt_with_empty_history_list_omits_history_section():
    prompt = compose_prompt("exec-1", "pergunta", history=[])

    assert "Etapas já executadas" not in prompt


def test_compose_prompt_includes_history_steps_in_order():
    step1 = ModelStep(
        execution_id="exec-1",
        action=Action.USE_TOOL,
        confidence=Confidence.LOW,
        reason="preciso pesquisar",
        tool="WEB_SEARCH",
        parameters={"query": "algo"},
    )
    step2 = ModelStep(
        execution_id="exec-1",
        action=Action.RESPOND,
        confidence=Confidence.HIGH,
        reason="já tenho a resposta",
    )
    history = [
        StepRecord(step=step1, observation="resultado da busca: algo encontrado"),
        StepRecord(step=step2),
    ]

    prompt = compose_prompt("exec-1", "pergunta original", history=history)

    assert "Etapas já executadas" in prompt
    first_pos = prompt.index("WEB_SEARCH")
    second_pos = prompt.index("já tenho a resposta")
    assert first_pos < second_pos  # ordem cronológica preservada
    assert "resultado da busca: algo encontrado" in prompt


def test_compose_prompt_history_step_without_observation_has_no_observation_line():
    step = ModelStep(
        execution_id="exec-1",
        action=Action.RESPOND,
        confidence=Confidence.HIGH,
        reason="direto",
    )
    history = [StepRecord(step=step)]

    prompt = compose_prompt("exec-1", "pergunta", history=history)

    assert "Resultado observado" not in prompt
