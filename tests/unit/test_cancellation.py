"""Testes unitários do cancelamento (TASK-030): CancellationToken e
Execution.cancel()."""

import pytest

from app.orchestrator.cancellation import CancellationToken
from app.orchestrator.execution import Execution, ExecutionStatus, InvalidExecutionStateError


def test_cancellation_token_starts_not_cancelled():
    token = CancellationToken()

    assert token.is_cancelled is False
    assert token.reason is None


def test_cancellation_token_cancel_sets_flag_and_reason():
    token = CancellationToken()

    token.cancel("usuário desistiu")

    assert token.is_cancelled is True
    assert token.reason == "usuário desistiu"


def test_cancellation_token_default_reason():
    token = CancellationToken()

    token.cancel()

    assert token.reason == "cancelado"


def test_cancellation_token_second_cancel_keeps_first_reason():
    token = CancellationToken()
    token.cancel("primeiro motivo")

    token.cancel("segundo motivo")

    assert token.reason == "primeiro motivo"


def test_execution_cancel_from_pending():
    execution = Execution.new(origin="chat")

    execution.cancel("cancelado antes de iniciar")

    assert execution.status == ExecutionStatus.CANCELLED
    assert execution.error == "cancelado antes de iniciar"
    assert execution.finished_at is not None
    assert execution.is_terminal is True


def test_execution_cancel_from_running():
    execution = Execution.new(origin="chat")
    execution.start()

    execution.cancel("timeout da aplicação")

    assert execution.status == ExecutionStatus.CANCELLED
    assert execution.error == "timeout da aplicação"


def test_execution_cancel_after_completed_raises():
    execution = Execution.new(origin="chat")
    execution.start()
    execution.complete("resposta")

    with pytest.raises(InvalidExecutionStateError):
        execution.cancel("tarde demais")


def test_execution_cancel_after_failed_raises():
    execution = Execution.new(origin="chat")
    execution.start()
    execution.fail("erro qualquer")

    with pytest.raises(InvalidExecutionStateError):
        execution.cancel("tarde demais")


def test_execution_cancel_twice_raises():
    execution = Execution.new(origin="chat")
    execution.cancel("primeiro cancelamento")

    with pytest.raises(InvalidExecutionStateError):
        execution.cancel("segundo cancelamento")


def test_cancelled_is_terminal():
    execution = Execution.new(origin="chat")
    execution.cancel("motivo")

    assert execution.is_terminal is True
