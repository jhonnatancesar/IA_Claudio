"""Testes unitários da geração de execution_id (TASK-021)."""

import json
import uuid

from app.llm.protocol_validator import validate_step
from app.orchestrator.execution import Execution, ExecutionStatus
from app.orchestrator.execution_id import generate_execution_id


def test_generate_execution_id_returns_valid_uuid_string():
    execution_id = generate_execution_id()

    parsed = uuid.UUID(execution_id)  # não deve levantar
    assert str(parsed) == execution_id


def test_generate_execution_id_is_unique_each_call():
    ids = {generate_execution_id() for _ in range(50)}

    assert len(ids) == 50


def test_execution_new_creates_pending_execution_with_valid_id():
    execution = Execution.new(origin="chat")

    assert execution.status == ExecutionStatus.PENDING
    uuid.UUID(execution.execution_id)  # não deve levantar


def test_execution_new_generates_different_ids_for_retries():
    """Reenvios/retries sempre geram um novo execution_id (seção 25 da
    especificação mestre) — nunca reaproveitam o de uma tentativa anterior."""
    first_attempt = Execution.new(origin="application")
    retry_attempt = Execution.new(origin="application")

    assert first_attempt.execution_id != retry_attempt.execution_id


def test_generated_execution_id_passes_protocol_semantic_validation():
    """Integração TASK-017/TASK-021: um execution_id gerado aqui precisa
    passar na checagem de formato UUID de validate_step (protocol_validator)."""
    execution_id = generate_execution_id()
    payload = {
        "execution_id": execution_id,
        "action": "RESPOND",
        "confidence": "HIGH",
        "reason": "resposta pronta",
    }

    step = validate_step(json.dumps(payload))

    assert step.execution_id == execution_id
