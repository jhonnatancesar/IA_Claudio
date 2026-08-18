"""Testes unitários do modelo RAW/PROVISIONAL/CONFIRMED (TASK-052) — só o
que não toca o banco (enum, validação de `content` vazio)."""

import pytest

from app.knowledge.knowledge_model import KnowledgeStatus, save_knowledge


def test_knowledge_status_has_exactly_three_values():
    assert {status.value for status in KnowledgeStatus} == {
        "RAW",
        "PROVISIONAL",
        "CONFIRMED",
    }


@pytest.mark.parametrize("content", ["", "   "])
def test_save_knowledge_rejects_empty_content(content):
    with pytest.raises(ValueError):
        save_knowledge(content)
