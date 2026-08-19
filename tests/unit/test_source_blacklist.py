"""Testes unitários da blacklist de fontes (TASK-064) — só validação de
`reason` vazio, sem tocar o banco."""

import pytest

from app.sources.source_registry import BlockOrigin, block_source, unblock_source


@pytest.mark.parametrize("reason", ["", "   "])
def test_block_source_rejects_empty_reason(reason):
    with pytest.raises(ValueError):
        block_source("00000000-0000-0000-0000-000000000000", BlockOrigin.ADMIN, reason)


@pytest.mark.parametrize("reason", ["", "   "])
def test_unblock_source_rejects_empty_reason(reason):
    with pytest.raises(ValueError):
        unblock_source("00000000-0000-0000-0000-000000000000", BlockOrigin.ADMIN, reason)
