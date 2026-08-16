"""Testes unitários do formato de resposta JSON padrão de erro (TASK-008).

Cobre: estrutura exata do JSON (seção 36 da especificação mestre), presença
condicional de `details`, serializabilidade e a exceção `ClaudiaoError` como
atalho para montar a resposta — conforme docs/ERROR_CATALOG.md.
"""

import json

from app.errors.catalog import MISSING_REQUIRED_FIELD, UNKNOWN_INTERNAL_ERROR
from app.errors.response import (
    ClaudiaoError,
    build_error_response,
    error_response_from_exception,
)


def test_build_error_response_matches_spec_example():
    response = build_error_response(MISSING_REQUIRED_FIELD, details={"field": "query"})

    assert response == {
        "success": False,
        "error": {
            "http_status": 400,
            "code": 1001,
            "message": "Campo obrigatório ausente",
            "details": {"field": "query"},
        },
    }


def test_build_error_response_omits_details_when_not_given():
    response = build_error_response(UNKNOWN_INTERNAL_ERROR)

    assert response["success"] is False
    assert "details" not in response["error"]
    assert response["error"]["code"] == 9000
    assert response["error"]["http_status"] == 500


def test_build_error_response_omits_details_when_empty_dict():
    response = build_error_response(UNKNOWN_INTERNAL_ERROR, details={})

    assert "details" not in response["error"]


def test_build_error_response_is_json_serializable():
    response = build_error_response(MISSING_REQUIRED_FIELD, details={"field": "query"})

    dumped = json.dumps(response)
    assert json.loads(dumped) == response


def test_claudiao_error_carries_definition_and_details():
    exc = ClaudiaoError(MISSING_REQUIRED_FIELD, details={"field": "query"})

    assert exc.definition is MISSING_REQUIRED_FIELD
    assert exc.details == {"field": "query"}
    assert "1001" in str(exc)
    assert "Campo obrigatório ausente" in str(exc)


def test_error_response_from_exception_matches_build_error_response():
    exc = ClaudiaoError(MISSING_REQUIRED_FIELD, details={"field": "query"})

    from_exception = error_response_from_exception(exc)
    direct = build_error_response(MISSING_REQUIRED_FIELD, details={"field": "query"})

    assert from_exception == direct


def test_error_response_from_exception_without_details():
    exc = ClaudiaoError(UNKNOWN_INTERNAL_ERROR)

    response = error_response_from_exception(exc)

    assert "details" not in response["error"]
