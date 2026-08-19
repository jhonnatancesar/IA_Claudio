"""Testes unitários do desbloqueio somente ADMIN (TASK-066) — só a
checagem de papel/validação, que acontece antes de qualquer acesso ao
banco."""

import pytest

from app.errors.response import ClaudiaoError
from app.sources.unblock_rule import admin_unblock_source


def test_non_admin_role_is_rejected_before_touching_db():
    with pytest.raises(ClaudiaoError):
        admin_unblock_source(
            "00000000-0000-0000-0000-000000000000",
            role="USER",
            responsible="usuario1",
            reason="motivo",
        )


def test_unknown_role_is_rejected():
    with pytest.raises(ClaudiaoError):
        admin_unblock_source(
            "00000000-0000-0000-0000-000000000000",
            role="SUPERUSER",
            responsible="alguem",
            reason="motivo",
        )
