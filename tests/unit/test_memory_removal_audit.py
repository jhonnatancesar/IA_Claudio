"""Testes unitários da auditoria de remoção de memória (TASK-051) — só a
validação que não toca o banco (`reason` vazio); dispatch real é teste de
integração, já que persiste dados."""

import pytest

from app.memory.memory_model import delete_memory


@pytest.mark.parametrize("reason", ["", "   "])
def test_delete_memory_rejects_empty_reason_before_touching_db(reason):
    with pytest.raises(ValueError):
        delete_memory("00000000-0000-0000-0000-000000000000", reason=reason)
