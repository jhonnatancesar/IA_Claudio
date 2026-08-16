"""Testes unitários do catálogo interno de erros (TASK-007).

Cobre: resolução de domínio pela faixa do código, validação de faixa ao registrar,
detecção de código duplicado, consulta por código e os erros seed da fundação —
conforme docs/ERROR_CATALOG.md.
"""

import pytest

from app.errors.catalog import (
    DuplicateErrorCodeError,
    ErrorCodeOutOfRangeError,
    ErrorDomain,
    INVALID_FIELD_VALUE,
    MISSING_REQUIRED_FIELD,
    UNKNOWN_INTERNAL_ERROR,
    all_errors,
    domain_for_code,
    get_error,
    register_error,
)


@pytest.mark.parametrize(
    "code,expected_domain",
    [
        (1001, ErrorDomain.VALIDATION),
        (1999, ErrorDomain.VALIDATION),
        (2000, ErrorDomain.AUTH),
        (3500, ErrorDomain.TOOLS_PROVIDERS),
        (4000, ErrorDomain.MODEL_ORCHESTRATOR),
        (5042, ErrorDomain.MEMORY_KNOWLEDGE),
        (6999, ErrorDomain.DATABASE),
        (7000, ErrorDomain.QUOTAS_PROCESSING),
        (8123, ErrorDomain.INTEGRATIONS_APPLICATIONS),
        (9000, ErrorDomain.INTERNAL_GENERIC),
    ],
)
def test_domain_for_code_resolves_correct_range(code, expected_domain):
    assert domain_for_code(code) == expected_domain


def test_domain_for_code_rejects_code_below_1000():
    with pytest.raises(ErrorCodeOutOfRangeError):
        domain_for_code(999)


def test_domain_for_code_rejects_code_above_9999():
    with pytest.raises(ErrorCodeOutOfRangeError):
        domain_for_code(10000)


def test_register_error_rejects_code_outside_declared_domain():
    with pytest.raises(ErrorCodeOutOfRangeError):
        register_error(ErrorDomain.AUTH, 1001, 400, "código de validação no domínio errado")


def test_register_error_rejects_duplicate_code():
    register_error(ErrorDomain.VALIDATION, 1900, 400, "primeiro registro")
    with pytest.raises(DuplicateErrorCodeError):
        register_error(ErrorDomain.VALIDATION, 1900, 400, "segundo registro, mesmo código")


def test_register_error_returns_definition_and_is_queryable():
    definition = register_error(ErrorDomain.DATABASE, 6900, 503, "erro de teste")
    assert get_error(6900) is definition
    assert definition.code == 6900
    assert definition.http_status == 503


def test_get_error_raises_key_error_for_unknown_code():
    with pytest.raises(KeyError):
        get_error(4999)


def test_seed_errors_from_foundation_are_registered():
    assert MISSING_REQUIRED_FIELD.code == 1001
    assert MISSING_REQUIRED_FIELD.http_status == 400
    assert INVALID_FIELD_VALUE.code == 1002
    assert UNKNOWN_INTERNAL_ERROR.code == 9000
    assert UNKNOWN_INTERNAL_ERROR.http_status == 500

    catalog = all_errors()
    assert catalog[1001] is MISSING_REQUIRED_FIELD
    assert catalog[1002] is INVALID_FIELD_VALUE
    assert catalog[9000] is UNKNOWN_INTERNAL_ERROR


def test_all_errors_returns_copy_not_live_registry():
    snapshot = all_errors()
    snapshot[9999] = MISSING_REQUIRED_FIELD  # não deve afetar o catálogo real
    with pytest.raises(KeyError):
        get_error(9999)
