"""Testes unitários da autenticação de aplicações na API HTTP (TASK-067)
— só a extração do token do header e o caso de ausência, sem tocar o
banco (chamar `authenticate_application` de verdade é teste de
integração)."""

import pytest

from app.api.auth import INVALID_API_KEY, get_current_application
from app.errors.response import ClaudiaoError


def test_missing_authorization_header_raises():
    with pytest.raises(ClaudiaoError) as exc_info:
        get_current_application(authorization=None)

    assert exc_info.value.definition == INVALID_API_KEY


def test_malformed_authorization_header_raises():
    with pytest.raises(ClaudiaoError):
        get_current_application(authorization="cldk_algumacoisa")


def test_empty_bearer_token_raises():
    with pytest.raises(ClaudiaoError):
        get_current_application(authorization="Bearer ")
