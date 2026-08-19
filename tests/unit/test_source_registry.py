"""Testes unitários do cadastro de fontes (TASK-059) — só validação de
`identifier` vazio, sem tocar o banco."""

import pytest

from app.sources.source_registry import SourceReputation, SourceType, register_source


@pytest.mark.parametrize("identifier", ["", "   "])
def test_register_source_rejects_empty_identifier(identifier):
    with pytest.raises(ValueError):
        register_source(identifier)


def test_source_type_has_exactly_three_values():
    assert {source_type.value for source_type in SourceType} == {
        "PRIMARY",
        "SECONDARY",
        "UNKNOWN",
    }


def test_source_reputation_has_exactly_three_values():
    assert {reputation.value for reputation in SourceReputation} == {
        "LOW",
        "MEDIUM",
        "HIGH",
    }
