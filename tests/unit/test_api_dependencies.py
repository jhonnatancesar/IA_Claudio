"""Testes unitários das dependências de execução da API (TASK-069) — só
`get_active_model`, sem tocar o banco nem a rede."""

import pytest

from app.api.dependencies import NO_ACTIVE_MODEL_CONFIGURED, get_active_model
from app.errors.response import ClaudiaoError


def test_get_active_model_raises_when_env_var_unset(monkeypatch):
    monkeypatch.delenv("CLAUDIAO_ACTIVE_MODEL", raising=False)

    with pytest.raises(ClaudiaoError) as exc_info:
        get_active_model()

    assert exc_info.value.definition == NO_ACTIVE_MODEL_CONFIGURED


def test_get_active_model_returns_configured_value(monkeypatch):
    monkeypatch.setenv("CLAUDIAO_ACTIVE_MODEL", "llama3.2")

    assert get_active_model() == "llama3.2"
