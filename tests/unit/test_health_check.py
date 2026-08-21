"""Testes unitários do health check (TASK-085) — só `HealthCheckResult.
healthy`, lógica pura sobre itens construídos à mão, sem tocar rede/banco."""

from app.observability.health_check import HealthCheckItem, HealthCheckResult, HealthCheckStatus


def _item(status: HealthCheckStatus) -> HealthCheckItem:
    return HealthCheckItem(name="teste", status=status)


def test_healthy_true_when_all_ok():
    result = HealthCheckResult(items=[_item(HealthCheckStatus.OK), _item(HealthCheckStatus.OK)])

    assert result.healthy is True


def test_healthy_true_when_ok_and_skipped_mixed():
    result = HealthCheckResult(
        items=[_item(HealthCheckStatus.OK), _item(HealthCheckStatus.SKIPPED)]
    )

    assert result.healthy is True


def test_healthy_false_when_any_failed():
    result = HealthCheckResult(
        items=[_item(HealthCheckStatus.OK), _item(HealthCheckStatus.FAILED)]
    )

    assert result.healthy is False


def test_healthy_true_for_empty_result():
    assert HealthCheckResult(items=[]).healthy is True
