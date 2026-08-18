"""Testes unitários de evidências/confiança/volatilidade de conhecimento
(TASK-056) — só o que não toca o banco (validação de `description`
vazia)."""

import pytest

from app.knowledge.knowledge_model import add_evidence


@pytest.mark.parametrize("description", ["", "   "])
def test_add_evidence_rejects_empty_description(description):
    with pytest.raises(ValueError):
        add_evidence("00000000-0000-0000-0000-000000000000", description)
