"""Testes unitários do versionamento de conhecimento (TASK-054) — só o
que não toca o banco (validação de `new_content`/`reason` vazios)."""

import pytest

from app.knowledge.knowledge_model import create_new_version


@pytest.mark.parametrize(
    "new_content,reason",
    [("", "motivo válido"), ("   ", "motivo válido")],
)
def test_create_new_version_rejects_empty_content(new_content, reason):
    with pytest.raises(ValueError):
        create_new_version(
            "00000000-0000-0000-0000-000000000000", new_content, reason
        )


@pytest.mark.parametrize("reason", ["", "   "])
def test_create_new_version_rejects_empty_reason(reason):
    with pytest.raises(ValueError):
        create_new_version(
            "00000000-0000-0000-0000-000000000000", "conteúdo novo", reason
        )
