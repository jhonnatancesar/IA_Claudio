"""Testes unitários de ExecutionPolicy (TASK-022)."""

import pytest

from app.policies.execution_policy import (
    DEFAULT_MAX_STEPS,
    ExecutionPolicy,
    InvalidExecutionPolicyError,
)


def test_direct_construction_with_valid_values():
    policy = ExecutionPolicy(web_search_allowed=True, max_steps=5, timeout_seconds=30.0)

    assert policy.web_search_allowed is True
    assert policy.max_steps == 5
    assert policy.timeout_seconds == 30.0


def test_default_max_steps_is_ten():
    policy = ExecutionPolicy(web_search_allowed=False)

    assert policy.max_steps == DEFAULT_MAX_STEPS == 10


def test_rejects_non_positive_max_steps():
    with pytest.raises(InvalidExecutionPolicyError):
        ExecutionPolicy(web_search_allowed=False, max_steps=0)


def test_rejects_negative_max_steps():
    with pytest.raises(InvalidExecutionPolicyError):
        ExecutionPolicy(web_search_allowed=False, max_steps=-1)


def test_rejects_non_positive_timeout_when_given():
    with pytest.raises(InvalidExecutionPolicyError):
        ExecutionPolicy(web_search_allowed=False, timeout_seconds=0)


def test_timeout_none_is_valid():
    policy = ExecutionPolicy(web_search_allowed=False, timeout_seconds=None)

    assert policy.timeout_seconds is None


def test_policy_is_immutable():
    policy = ExecutionPolicy(web_search_allowed=False)

    with pytest.raises(AttributeError):
        policy.max_steps = 20


def test_for_chat_has_no_fixed_timeout():
    policy = ExecutionPolicy.for_chat()

    assert policy.timeout_seconds is None


def test_for_chat_search_not_pre_authorized_by_default():
    policy = ExecutionPolicy.for_chat()

    assert policy.web_search_allowed is False


def test_for_chat_uses_default_max_steps():
    policy = ExecutionPolicy.for_chat()

    assert policy.max_steps == DEFAULT_MAX_STEPS


def test_for_application_requires_timeout():
    with pytest.raises(InvalidExecutionPolicyError):
        ExecutionPolicy.for_application(timeout_seconds=None)


def test_for_application_sets_given_timeout():
    policy = ExecutionPolicy.for_application(timeout_seconds=60.0)

    assert policy.timeout_seconds == 60.0


def test_for_application_can_authorize_search():
    policy = ExecutionPolicy.for_application(timeout_seconds=60.0, web_search_allowed=True)

    assert policy.web_search_allowed is True


def test_for_application_respects_custom_max_steps():
    policy = ExecutionPolicy.for_application(timeout_seconds=60.0, max_steps=25)

    assert policy.max_steps == 25
