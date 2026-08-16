"""Testes unitários de autorização por papel (TASK-010)."""

import pytest

from app.auth.roles import FORBIDDEN_ADMIN_ONLY, Role, is_admin, require_admin
from app.auth.users import VALID_ROLES
from app.errors.response import ClaudiaoError


def test_role_enum_has_exactly_admin_and_user():
    assert {role.value for role in Role} == {"ADMIN", "USER"}


def test_users_valid_roles_derives_from_role_enum():
    assert set(VALID_ROLES) == {role.value for role in Role}


def test_is_admin_true_for_admin_role():
    assert is_admin("ADMIN") is True
    assert is_admin(Role.ADMIN.value) is True


def test_is_admin_false_for_user_role():
    assert is_admin("USER") is False


def test_is_admin_false_for_unknown_role():
    assert is_admin("SUPERUSER") is False


def test_require_admin_passes_silently_for_admin():
    require_admin("ADMIN")  # não deve levantar


def test_require_admin_raises_for_non_admin():
    with pytest.raises(ClaudiaoError) as exc_info:
        require_admin("USER")

    assert exc_info.value.definition is FORBIDDEN_ADMIN_ONLY
    assert exc_info.value.definition.http_status == 403


def test_require_admin_carries_details_into_error():
    with pytest.raises(ClaudiaoError) as exc_info:
        require_admin("USER", details={"username": "fulano"})

    assert exc_info.value.details == {"username": "fulano"}
