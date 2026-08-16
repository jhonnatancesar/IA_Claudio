"""Testes unitários do modelo de Execution (TASK-020): estados válidos,
transições inválidas e o ciclo completo (criar → iniciar → etapas → concluir).
"""

import pytest

from app.llm.protocol import Action, Confidence, ModelStep
from app.orchestrator.execution import (
    Execution,
    ExecutionStatus,
    InvalidExecutionStateError,
)


def _make_step(reason: str = "etapa de teste") -> ModelStep:
    return ModelStep(
        execution_id="exec-1",
        action=Action.RESPOND,
        confidence=Confidence.HIGH,
        reason=reason,
    )


def test_execution_starts_as_pending():
    execution = Execution(execution_id="exec-1", origin="chat")

    assert execution.status == ExecutionStatus.PENDING
    assert execution.step_count == 0
    assert execution.is_terminal is False


def test_execution_rejects_empty_execution_id():
    with pytest.raises(ValueError):
        Execution(execution_id="", origin="chat")


def test_execution_rejects_empty_origin():
    with pytest.raises(ValueError):
        Execution(execution_id="exec-1", origin="  ")


def test_start_transitions_to_running():
    execution = Execution(execution_id="exec-1", origin="chat")

    execution.start()

    assert execution.status == ExecutionStatus.RUNNING


def test_start_twice_raises():
    execution = Execution(execution_id="exec-1", origin="chat")
    execution.start()

    with pytest.raises(InvalidExecutionStateError):
        execution.start()


def test_add_step_before_start_raises():
    execution = Execution(execution_id="exec-1", origin="chat")

    with pytest.raises(InvalidExecutionStateError):
        execution.add_step(_make_step())


def test_add_step_while_running_appends():
    execution = Execution(execution_id="exec-1", origin="chat")
    execution.start()

    execution.add_step(_make_step("primeira"))
    execution.add_step(_make_step("segunda"))

    assert execution.step_count == 2
    assert execution.steps[0].reason == "primeira"
    assert execution.steps[1].reason == "segunda"


def test_complete_sets_result_and_finished_at():
    execution = Execution(execution_id="exec-1", origin="chat")
    execution.start()

    execution.complete("resposta final")

    assert execution.status == ExecutionStatus.COMPLETED
    assert execution.result == "resposta final"
    assert execution.finished_at is not None
    assert execution.is_terminal is True


def test_complete_before_start_raises():
    execution = Execution(execution_id="exec-1", origin="chat")

    with pytest.raises(InvalidExecutionStateError):
        execution.complete("resposta")


def test_complete_twice_raises():
    execution = Execution(execution_id="exec-1", origin="chat")
    execution.start()
    execution.complete("resposta")

    with pytest.raises(InvalidExecutionStateError):
        execution.complete("outra resposta")


def test_fail_sets_error_and_finished_at():
    execution = Execution(execution_id="exec-1", origin="chat")
    execution.start()

    execution.fail("provedor indisponível")

    assert execution.status == ExecutionStatus.FAILED
    assert execution.error == "provedor indisponível"
    assert execution.finished_at is not None
    assert execution.is_terminal is True


def test_fail_from_pending_is_allowed():
    """Falhar antes mesmo de iniciar é válido (ex.: erro de validação antes
    da execução começar de fato)."""
    execution = Execution(execution_id="exec-1", origin="chat")

    execution.fail("payload inválido")

    assert execution.status == ExecutionStatus.FAILED


def test_fail_after_completed_raises():
    execution = Execution(execution_id="exec-1", origin="chat")
    execution.start()
    execution.complete("resposta")

    with pytest.raises(InvalidExecutionStateError):
        execution.fail("erro tardio")


def test_add_step_after_completed_raises():
    execution = Execution(execution_id="exec-1", origin="chat")
    execution.start()
    execution.complete("resposta")

    with pytest.raises(InvalidExecutionStateError):
        execution.add_step(_make_step())


def test_full_cycle_create_start_steps_complete():
    execution = Execution(execution_id="exec-full-cycle", origin="application")

    assert execution.status == ExecutionStatus.PENDING

    execution.start()
    assert execution.status == ExecutionStatus.RUNNING

    execution.add_step(
        ModelStep(
            execution_id="exec-full-cycle",
            action=Action.USE_TOOL,
            confidence=Confidence.LOW,
            reason="preciso pesquisar",
            tool="WEB_SEARCH",
            parameters={"query": "algo"},
        )
    )
    execution.add_step(_make_step("agora sei a resposta"))
    assert execution.step_count == 2

    execution.complete("resposta final composta a partir das etapas")

    assert execution.status == ExecutionStatus.COMPLETED
    assert execution.is_terminal is True
    assert execution.result == "resposta final composta a partir das etapas"
    assert execution.finished_at is not None
    assert execution.finished_at >= execution.created_at
