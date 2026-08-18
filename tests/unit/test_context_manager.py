"""Testes unitários do modelo de `ContextManager` (TASK-037)."""

import pytest

from app.context.context_manager import ContextManager


def test_new_creates_empty_context_for_conversation():
    context = ContextManager.new("conv-1")

    assert context.conversation_id == "conv-1"
    assert context.active_topic is None
    assert context.recent_entities == []
    assert context.current_objective is None
    assert context.recent_actions == []
    assert context.implicit_references == {}
    assert context.corrections == []


def test_rejects_empty_conversation_id():
    with pytest.raises(ValueError):
        ContextManager(conversation_id="")


def test_rejects_blank_conversation_id():
    with pytest.raises(ValueError):
        ContextManager(conversation_id="   ")


def test_two_contexts_do_not_share_mutable_defaults():
    context_a = ContextManager.new("conv-a")
    context_b = ContextManager.new("conv-b")

    context_a.recent_entities.append("entidade-x")

    assert context_a.recent_entities == ["entidade-x"]
    assert context_b.recent_entities == []


def test_set_active_topic_defines_topic():
    context = ContextManager.new("conv-1")

    context.set_active_topic("previsão do tempo")

    assert context.active_topic == "previsão do tempo"


def test_set_active_topic_replaces_previous_topic():
    context = ContextManager.new("conv-1")
    context.set_active_topic("assunto antigo")

    context.set_active_topic("assunto novo")

    assert context.active_topic == "assunto novo"


@pytest.mark.parametrize("topic", ["", "   "])
def test_set_active_topic_rejects_empty_topic(topic):
    context = ContextManager.new("conv-1")

    with pytest.raises(ValueError):
        context.set_active_topic(topic)


def test_track_entity_adds_entity_as_most_recent():
    context = ContextManager.new("conv-1")

    context.track_entity("Ollama")
    context.track_entity("PostgreSQL")

    assert context.recent_entities == ["PostgreSQL", "Ollama"]


def test_track_entity_moves_existing_entity_to_front_without_duplicating():
    context = ContextManager.new("conv-1")
    context.track_entity("Ollama")
    context.track_entity("PostgreSQL")

    context.track_entity("Ollama")

    assert context.recent_entities == ["Ollama", "PostgreSQL"]


@pytest.mark.parametrize("entity", ["", "   "])
def test_track_entity_rejects_empty_entity(entity):
    context = ContextManager.new("conv-1")

    with pytest.raises(ValueError):
        context.track_entity(entity)


def test_set_and_resolve_implicit_reference():
    context = ContextManager.new("conv-1")

    context.set_implicit_reference("esse", "PostgreSQL")

    assert context.resolve_reference("esse") == "PostgreSQL"


def test_set_implicit_reference_replaces_previous_association():
    context = ContextManager.new("conv-1")
    context.set_implicit_reference("esse", "PostgreSQL")

    context.set_implicit_reference("esse", "Ollama")

    assert context.resolve_reference("esse") == "Ollama"


def test_resolve_reference_returns_none_when_unresolved():
    context = ContextManager.new("conv-1")

    assert context.resolve_reference("esse") is None


@pytest.mark.parametrize("reference,entity", [("", "PostgreSQL"), ("esse", "")])
def test_set_implicit_reference_rejects_empty_values(reference, entity):
    context = ContextManager.new("conv-1")

    with pytest.raises(ValueError):
        context.set_implicit_reference(reference, entity)


def test_record_correction_appends_in_chronological_order():
    context = ContextManager.new("conv-1")

    context.record_correction("não é PostgreSQL, é MySQL")
    context.record_correction("na verdade é MariaDB")

    assert context.corrections == [
        "não é PostgreSQL, é MySQL",
        "na verdade é MariaDB",
    ]


@pytest.mark.parametrize("correction", ["", "   "])
def test_record_correction_rejects_empty_correction(correction):
    context = ContextManager.new("conv-1")

    with pytest.raises(ValueError):
        context.record_correction(correction)
