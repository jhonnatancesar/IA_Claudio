"""Testes unitários do monitor de janela de contexto (TASK-042)."""

import pytest

from app.context.context_window import ContextWindowMonitor, InvalidContextWindowError


def test_usage_ratio_computes_fraction_used():
    monitor = ContextWindowMonitor(capacity=1000)

    assert monitor.usage_ratio(250) == 0.25


def test_usage_ratio_can_exceed_one_when_over_capacity():
    monitor = ContextWindowMonitor(capacity=1000)

    assert monitor.usage_ratio(1500) == 1.5


def test_is_full_true_at_or_above_capacity():
    monitor = ContextWindowMonitor(capacity=1000)

    assert monitor.is_full(1000) is True
    assert monitor.is_full(1500) is True


def test_is_full_false_below_capacity():
    monitor = ContextWindowMonitor(capacity=1000)

    assert monitor.is_full(999) is False


@pytest.mark.parametrize("capacity", [0, -1])
def test_rejects_non_positive_capacity(capacity):
    with pytest.raises(InvalidContextWindowError):
        ContextWindowMonitor(capacity=capacity)


def test_rejects_negative_tokens_used():
    monitor = ContextWindowMonitor(capacity=1000)

    with pytest.raises(InvalidContextWindowError):
        monitor.usage_ratio(-1)
