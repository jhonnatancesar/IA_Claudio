"""Testes unitários do monitor de janela de contexto (TASK-042)."""

import pytest

from app.context.context_window import (
    DEFAULT_WARNING_THRESHOLD,
    ContextWindowMonitor,
    InvalidContextWindowError,
)


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


def test_default_warning_threshold_is_eighty_percent():
    assert DEFAULT_WARNING_THRESHOLD == 0.8


def test_requires_warning_false_below_threshold():
    monitor = ContextWindowMonitor(capacity=1000)

    assert monitor.requires_warning(799) is False


def test_requires_warning_true_at_threshold():
    monitor = ContextWindowMonitor(capacity=1000)

    assert monitor.requires_warning(800) is True


def test_requires_warning_stays_true_past_full():
    monitor = ContextWindowMonitor(capacity=1000)

    assert monitor.requires_warning(1500) is True


def test_requires_warning_accepts_custom_threshold():
    monitor = ContextWindowMonitor(capacity=1000)

    assert monitor.requires_warning(500, threshold=0.5) is True
    assert monitor.requires_warning(499, threshold=0.5) is False
