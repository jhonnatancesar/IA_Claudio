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
